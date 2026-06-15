# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. 

# SPDX-License-Identifier: Apache-2.0. 

#AWS Server: us-east-1 

import json 

import time 

import sys 

import threading 

import requests 

import serial 

import xml.etree.ElementTree as ET 

from awscrt import mqtt, http 

from awsiot import mqtt_connection_builder 

from command_line_utils import CommandLineUtils 

 

# --- USER CONFIGURATION --- 

SERIAL_PORT = 'COM3'  # <--- CHANGE THIS TO YOUR ARDUINO PORT 

BAUD_RATE = 9600 

MIC_DATA_FILE = "mic_data_log.txt" 

 

# --- MTConnect Configuration --- 

MTCONNECT_URL = "http://192.168.53.2:8082/VF-4SS/current" 

NAMESPACES = {'m': 'urn:mtconnect.org:MTConnectStreams:1.2'} 

DATA_ITEM_MAP = { 

    "spindle_speed": "sspeed", 

    "spindle_enabled": "sp1enabled", 

    "x_axis_acutal_position": "x_axis_actual_position", 

    "y_axis_actual_position": "y_axis_actual_position", 

    "z_axis_actual_position": "z_axis_actual_position", 

    "controller_mode": "mode", 

    "execution_status": "rstat", 

    "feedrate_override": "fdovrd", 

    "rapid_override": "rovrd", 

} 

PARSE_ID_MAP = {v: k for k, v in DATA_ITEM_MAP.items()} 

 

# --- Helper Functions --- 

 

def fetch_mtconnect_data(): 

    """Fetches and parses MTConnect XML.""" 

    data = {} 

    try: 

        response = requests.get(MTCONNECT_URL, timeout=0.09) 

        response.raise_for_status() 

        xml_root = ET.fromstring(response.content) 

 

        path = "./m:Streams/m:DeviceStream//*[@dataItemId]" 

        items = xml_root.findall(path, NAMESPACES) 

 

        latest_values = {} 

        for item in items: 

            item_id = item.get('dataItemId') 

            if item_id in PARSE_ID_MAP: 

                key_name = PARSE_ID_MAP[item_id] 

                latest_values[key_name] = item.text 

 

        for key in DATA_ITEM_MAP.keys(): 

            data[key] = latest_values.get(key, None) 

        return data 

    except Exception as e: 

        print(f"[MTConnect Error] {e}") 

        return None 

 

def convert_to_float(value, default=0.0): 

    if value is None: return default 

    try: return float(value) 

    except (ValueError, TypeError): return default 

 

def convert_to_bool(value, default=False): 

    if value is None: return default 

    return str(value).lower() == 'true' 

 

def convert_to_string(value, default=""): 

    if value is None: return default 

    return str(value) 

 

# --- AWS IoT Callbacks --- 

 

cmdData = CommandLineUtils.parse_sample_input_pubsub() 

received_count = 0 

received_all_event = threading.Event() 

 

def on_connection_interrupted(connection, error, **kwargs): 

    print("Connection interrupted. error: {}".format(error)) 

 

def on_connection_resumed(connection, return_code, session_present, **kwargs): 

    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present)) 

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present: 

        print("Session did not persist. Resubscribing to existing topics...") 

        resubscribe_future, _ = connection.resubscribe_existing_topics() 

        resubscribe_future.add_done_callback(on_resubscribe_complete) 

 

def on_resubscribe_complete(resubscribe_future): 

    resubscribe_results = resubscribe_future.result() 

    print("Resubscribe results: {}".format(resubscribe_results)) 

    for topic, qos in resubscribe_results['topics']: 

        if qos is None: 

            sys.exit("Server rejected resubscribe to topic: {}".format(topic)) 

 

def on_message_received(topic, payload, dup, qos, retain, **kwargs): 

    print("Received message from topic '{}': {}".format(topic, payload)) 

    global received_count 

    received_count += 1 

    if received_count == cmdData.input_count: 

        received_all_event.set() 

 

def on_connection_success(connection, callback_data): 

    assert isinstance(callback_data, mqtt.OnConnectionSuccessData) 

    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present)) 

 

def on_connection_failure(connection, callback_data): 

    assert isinstance(callback_data, mqtt.OnConnectionFailuredata) 

    print("Connection failed with error code: {}".format(callback_data.error)) 

 

def on_connection_closed(connection, callback_data): 

    print("Connection closed") 

 

if __name__ == '__main__': 

    # 1. Setup Serial Connection 

    print(f"Connecting to Arduino on {SERIAL_PORT}...") 

    try: 

        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) 

        time.sleep(2) # Allow Arduino reset 

        print("Serial connection established.") 

    except Exception as e: 

        print(f"Error connecting to Serial Port: {e}") 

        sys.exit(1) 

 

    # 2. Setup AWS Connection 

    proxy_options = None 

    if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0: 

        proxy_options = http.HttpProxyOptions( 

            host_name=cmdData.input_proxy_host, 

            port=cmdData.input_proxy_port) 

 

    mqtt_connection = mqtt_connection_builder.mtls_from_path( 

        endpoint=cmdData.input_endpoint, 

        port=cmdData.input_port, 

        cert_filepath=cmdData.input_cert, 

        pri_key_filepath=cmdData.input_key, 

        ca_filepath=cmdData.input_ca, 

        on_connection_interrupted=on_connection_interrupted, 

        on_connection_resumed=on_connection_resumed, 

        client_id=cmdData.input_clientId, 

        clean_session=False, 

        keep_alive_secs=30, 

        http_proxy_options=proxy_options, 

        on_connection_success=on_connection_success, 

        on_connection_failure=on_connection_failure, 

        on_connection_closed=on_connection_closed) 

 

    if not cmdData.input_is_ci: 

        print(f"Connecting to {cmdData.input_endpoint} with client ID '{cmdData.input_clientId}'...") 

    else: 

        print("Connecting to endpoint with client ID") 

     

    connect_future = mqtt_connection.connect() 

    connect_future.result() 

    print("Connected!") 

 

    message_count = cmdData.input_count 

    message_topic = cmdData.input_topic 

 

    # Subscribe 

    print("Subscribing to topic '{}'...".format(message_topic)) 

    subscribe_future, packet_id = mqtt_connection.subscribe( 

        topic=message_topic, 

        qos=mqtt.QoS.AT_LEAST_ONCE, 

        callback=on_message_received) 

    subscribe_result = subscribe_future.result() 

    print("Subscribed with {}".format(str(subscribe_result['qos']))) 

 

    # 3. MAIN LOOP: Read Sensor -> Fetch MTConnect -> Publish 

    if message_count == 0: 

        print("Sending messages until program killed") 

    else: 

        print("Sending {} message(s)".format(message_count)) 

 

    publish_count = 1 

    prev_payload = {} 

     

    # Open file for logging 

    try: 

        with open(MIC_DATA_FILE, 'a') as log_file: 

            while (publish_count <= message_count) or (message_count == 0): 

                 

                loop_start_time = time.time() 

                mic_value = 0.0 

 

                # --- A. Read Arduino --- 

                if ser.in_waiting > 0: 

                    try: 

                        raw_line = ser.readline().decode('utf-8').strip() 

                        if raw_line: 

                            mic_value = float(raw_line) 

                            # Log to file 

                            log_entry = json.dumps({"mic": mic_value}) 

                            log_file.write(log_entry + "\n") 

                            log_file.flush() 

                    except ValueError: 

                        pass 

                 

                # --- B. Read MTConnect --- 

                cnc_data = fetch_mtconnect_data() 

                if not cnc_data: 

                     cnc_data = {key: prev_payload.get(key, None) for key in DATA_ITEM_MAP.keys()} 

 

                # --- C. Build Payload --- 

                payload = {} 

                payload["timestamp"] = loop_start_time 

                payload["mic"] = mic_value 

                 

                # Map CNC Data 

                payload["spindle_speed"] = convert_to_float(cnc_data.get("spindle_speed")) 

                payload["spindle_enabled"] = convert_to_bool(cnc_data.get("spindle_enabled")) 

                payload["x_axis_acutal_position"] = convert_to_float(cnc_data.get("x_axis_acutal_position")) 

                payload["y_axis_actual_position"] = convert_to_float(cnc_data.get("y_axis_actual_position")) 

                payload["z_axis_actual_position"] = convert_to_float(cnc_data.get("z_axis_actual_position")) 

                payload["controller_mode"] = convert_to_string(cnc_data.get("controller_mode")) 

                payload["execution_status"] = convert_to_string(cnc_data.get("execution_status")) 

                payload["feedrate_override"] = convert_to_float(cnc_data.get("feedrate_override")) 

                payload["rapid_override"] = convert_to_float(cnc_data.get("rapid_override")) 

 

                # Calculate Deltas 

                keys_to_process = list(payload.keys()) 

                if prev_payload: 

                    for key in keys_to_process: 

                        if key == "timestamp": continue 

                        current_val = payload[key] 

                        prev_val = prev_payload.get(key, current_val) 

                         

                        if isinstance(current_val, (bool, str)): 

                            delta = 1 if current_val != prev_val else 0 

                        else: 

                            delta = current_val - prev_val 

                        payload[f"delta_{key}"] = delta 

                else: 

                     for key in keys_to_process: 

                        if key != "timestamp": payload[f"delta_{key}"] = 0 

 

                # --- D. Publish to AWS --- 

                message_json = json.dumps(payload) 

                print(f"Publishing [{publish_count}]: {message_json}") 

                 

                mqtt_connection.publish( 

                    topic=message_topic, 

                    payload=message_json, 

                    qos=mqtt.QoS.AT_LEAST_ONCE) 

                 

                prev_payload = payload.copy() 

                publish_count += 1 

                 

                # Wait 0.1s (to match sampling rate) 

                time.sleep(1.5) 

 

    except KeyboardInterrupt: 

        print("Stopping...") 

    finally: 

        ser.close() 

 

    # Wait for all messages to be received. 

    if message_count != 0 and not received_all_event.is_set(): 

        print("Waiting for all messages to be received...") 

 

    received_all_event.wait() 

    print("{} message(s) received.".format(received_count)) 

 

    # Disconnect 

    print("Disconnecting...") 

    disconnect_future = mqtt_connection.disconnect() 

    disconnect_future.result() 

    print("Disconnected!") 

 