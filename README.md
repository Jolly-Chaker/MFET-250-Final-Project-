# MFET 250 Final Project - Smart CNC Process Monitoring with AWS IoT and Machine Learning

Team Size: 3 students per team 
Duration: ≈ 5 weeks 
Hardware: Haas VF-4SS CNC machine + external microphone sensor 
Cloud Platform: AWS IoT Core · AWS Database (DynamoDB) · AWS Lambda 
ML Environment: Google Colab 

# Project Overview 

Students will design and implement a cloud-connected smart manufacturing system to monitor and classify CNC machine states using real-time data. Each team will: 
  1. Collect real-time data from the CNC controller (via MTConnect) and an external microphone sensor. 
  2. Stream combined data to AWS IoT Core every 0.1 s. 
  3. Store and manage data in AWS database services. 
  4. Train a machine-learning model in Google Colab to predict machine status (Cutting / Travel / Idle). 
  5. Deploy the trained model on AWS Lambda for real-time inference and demo. 

# Project Tasks 

# Task 1 – Project Planning and Architecture 
Form teams of 2 and design system architecture. Define data flow: CNC → MTConnect/Sensor → IoT Core → Database → Colab → Lambda → Dashboard. Identify AWS services to be used and assign team roles. 

Deliverables: 
  - Short project introduction 
  - System architecture diagram (flowchart or block diagram) 

# Task 2 – Data Acquisition and IoT Integration 
Test a microphone sensor, and upload the value to IoT core, using the JSON format as: 

{ 
  “timestamp”: 1762369455.797889, 
  “mic”: 56 
} 

Configure the MTConnect client to access controller data from http://192.168.53.2:8082/VF-4SS/current. Extract key data from the controller (timestamp, spindle speed, spindle_enabled, spindle load, axis load, axis positions, and others). Write a Python script to combine CNC + acoustic data every 0.1 s and publish to AWS IoT Core via MQTT (each MQTT message contains two sets of values, including current sensor data and value change compared to the previous message).  

{ 
“timestamp”: 1762369455.797889, 
“mic”: 56, 
“x_axis_acutal_position”: 3.23, 
…. 
“delta_mic”: -2, 
“delta_x_axis_acutal_position”: 0.1, 
…. 
} 

Deliverables: 
  - Data collection script (.py) 
  - Two sample data files (1 minute each) 
  - Screenshot of live IoT Core message stream 

# Task 3 – Cloud Database Setup and IoT Routing 
Create an AWS database (DynamoDB), where the Partition Key is named as timestamp, (Number), Sort Key is not needed. Configure an IoT Rule Engine SQL statement to route incoming IoT messages to the database (Choose “DynamoDBv2” in the rule actions). Test data insertion using simulated messages via MQTT test client.  

Deliverables: 
  - Screenshot of database and IoT Rule configuration 
  - Brief write-up of IoT Rule SQL statement. 
  - Send testing data to the database. 
  - Download the testing dataset as CSV. 

# Task 4 – Continuous Data Collection and Export 
During actual CNC machining, enable continuous data logging from MTConnect + microphone. Verify that new entries appear in the database in real time. After recording a full machining session, export the data to CSV for analysis and ML training. The data collection contains three stages: cutting, traveling, and idle. These stages are the labels for the data collected. Students need to record the starting time of each stage (the instructor will prompt the timing). 

Deliverables: 
  - Screenshot showing live data updates in AWS DB 
  - Exported CSV dataset (≥ 10 minutes runtime) 
  - Short note describing data fields and sampling rate 

# Task 5 – Machine Learning Model (Colab) 
Clean the CSV data, and label machine states (Cutting / Travel / Idle) based on timestamp. Extract features (spindle speed, spindle_enabled, spindle load, axis load, axis positions, mic acoustic value, and others). Using Colab, train and evaluate a classification model (Random Forest recommended). Target accuracy ≥ 80%. Save trained model (.json). 

Deliverables: 
  - Google Colab notebook (.ipynb) with plots and confusion matrix 
  - Trained model file for deployment 

# Task 6 – Deployment and Demo 
Deploy the trained model on AWS Lambda. During demo, the instructor runs a new machining process; Lambda performs real-time classification every 0.1 s. In the Lambda function, the classification results will be sent to two locations: (1) the MQTT test client, and (2) a new table in the database DynamoDB to store the timestamp as the Partition Key and classification result. Display predicted status on the MQTT test client in real-time. The new table database will be exported as a CSV file and visualized in Excel.  

Deliverables: 
  - Lambda function code and execution screenshot (MQTT test client, Database, and Excel) 
  - Demo PowerPoint presentation (10–12 slides) 
  - Final project report (4–6 pages, PDF) 
