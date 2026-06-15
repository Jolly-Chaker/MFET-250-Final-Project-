import json 

import time 

import sys 

import requests 

import xml.etree.ElementTree as ET 

import serial  # <--- ADDED FOR ARDUINO 

 #AWS Server: us-east-1

# --- Configuration --- 

# REPLACE 'COM3' with your actual Arduino port 

SERIAL_PORT = 'COM3'  
BAUD_RATE = 9600 
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
# --- Mic Data File for Logging --- 
MIC_DATA_FILE = "mic_data_log.txt" 

def fetch_mtconnect_data(): 

    """ 

    Fetches and parses MTConnect XML. 

    Returns a dictionary with the keys defined in DATA_ITEM_MAP. 

    """ 

    data = {} 

    try: 

        response = requests.get(MTCONNECT_URL, timeout=0.09) # 90ms timeout 

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

 

    except requests.exceptions.RequestException: 

        return None  

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

 

def main(): 

     

    # --- 1. Initialize Serial Connection --- 

    print(f"Connecting to Arduino on {SERIAL_PORT}...") 

    try: 

        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) 

        time.sleep(2) # Wait for Arduino to reset 

        print("Serial connection established.") 

    except Exception as e: 

        print(f"Error connecting to Serial Port: {e}") 

        sys.exit(1) 

 

    print(f"Opening {MIC_DATA_FILE} for logging...") 

     

    # Open file in APPEND mode so we don't overwrite immediately,  

    # or 'w' if you want a fresh file every run. 

    with open(MIC_DATA_FILE, 'a') as log_file:  

 

        # --- 2. Main Loop: Read Live, Fetch, Combine, Print --- 

        print(f"Reading LIVE data. Press CTRL+C to stop.") 

         

        prev_payload = {} 

         

        try: 

            while True: # Infinite loop for live data 

                loop_start_time = time.time() 

                 

                # --- A. Read Live Mic Data from Arduino --- 

                if ser.in_waiting > 0: 

                    try: 

                        # Read line, decode, strip whitespace 

                        raw_line = ser.readline().decode('utf-8').strip() 

                         

                        # Handle empty lines 

                        if not raw_line: 

                            continue 

 

                        # Convert to valid data type (assuming float or int) 

                        mic_value = float(raw_line) 

 

                        # --- LOG TO FILE --- 

                        # Saving in the same format as the previous script expected: {"mic": value} 

                        log_entry = json.dumps({"mic": mic_value}) 

                        log_file.write(log_entry + "\n") 

                        log_file.flush() # Ensure it writes to disk immediately 

 

                    except ValueError: 

                        # Initial serial data might be garbage, skip it 

                        continue 

                else: 

                    # If no data is waiting, skip this loop iteration or wait slightly 

                    time.sleep(0.01) 

                    continue 

 

                # --- B. Get MTConnect Data --- 

                cnc_data = fetch_mtconnect_data() 

                if not cnc_data: 

                    # If fetch fails, use previous values 

                    cnc_data = {key: prev_payload.get(key, None) for key in DATA_ITEM_MAP.keys()} 

 

                # --- C. Build Payload --- 

                payload = {} 

                payload["timestamp"] = loop_start_time 

                payload["mic"] = mic_value 

                 

                payload["spindle_speed"] = convert_to_float(cnc_data.get("spindle_speed")) 

                payload["spindle_enabled"] = convert_to_bool(cnc_data.get("spindle_enabled")) 

                payload["x_axis_acutal_position"] = convert_to_float(cnc_data.get("x_axis_acutal_position")) 

                payload["y_axis_actual_position"] = convert_to_float(cnc_data.get("y_axis_actual_position")) 

                payload["z_axis_actual_position"] = convert_to_float(cnc_data.get("z_axis_actual_position")) 

                payload["controller_mode"] = convert_to_string(cnc_data.get("controller_mode")) 

                payload["execution_status"] = convert_to_string(cnc_data.get("execution_status")) 

                payload["feedrate_override"] = convert_to_float(cnc_data.get("feedrate_override")) 

                payload["rapid_override"] = convert_to_float(cnc_data.get("rapid_override")) 

                 

                # --- D. Calculate Deltas --- 

                keys_to_process = list(payload.keys()) 

                 

                if prev_payload: 

                    for key in keys_to_process: 

                        if key == "timestamp": continue 

                         

                        current_val = payload[key] 

                        prev_val = prev_payload.get(key, current_val) 

                         

                        if isinstance(current_val, bool): 

                            delta = 1 if current_val != prev_val else 0 

                        elif isinstance(current_val, str): 

                            delta = 1 if current_val != prev_val else 0 

                        else: 

                            delta = current_val - prev_val 

                         

                        payload[f"delta_{key}"] = delta 

                else: 

                    # First loop, all deltas are 0 

                    for key in keys_to_process: 

                        if key != "timestamp": 

                            payload[f"delta_{key}"] = 0 

                 

                # --- E. VERIFY: Print the data --- 

                payload_json = json.dumps(payload, indent=2) 

                print("--- Verifying Live JSON Payload ---") 

                print(payload_json) 

                print("------------------------------") 

 

                prev_payload = payload.copy() 

 

                # --- Wait for interval --- 

                # We adjust sleep based on how long processing took 

                time_to_wait = (loop_start_time + 0.1) - time.time() 

                if time_to_wait > 0: 

                    time.sleep(time_to_wait) 

 

        except KeyboardInterrupt: 

            print("\nStopping script...") 

        finally: 

            ser.close() 

            print("Serial connection closed. Done.") 

 

if __name__ == "__main__": 

    main() 

 