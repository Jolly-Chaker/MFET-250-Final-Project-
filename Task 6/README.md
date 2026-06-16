# AWS Lambda Integration 

Following the successful training of the model, the focus shifted to cloud deployment to enable real-time predictions. 

Function Development: We utilized AWS Lambda to host the serverless inference engine. Using AI-assisted programming, we generated the initial Lambda handler function that can accept sensor inputs and output state predictions. 

Iterative Enhancements: The function underwent several iterations to meet system requirements. We expanded its capabilities to perform two simultaneous actions upon generating a prediction: 

Real-Time Monitoring: Publishing the result to a specific MQTT topic for immediate live viewing. 

Data Persistence: Writing the prediction and timestamp to a DynamoDB table for archival and historical analysis. 
Final Testing and Visualization 

To validate the end-to-end system, we conducted a full operational test and subsequently analyzed the data stored in the cloud. 

Data Extraction & Visualization: We exported the logged data from the newly created DynamoDB table. Using a custom Python script generated with AI assistance, we processed this data to generate a time-series line graph. 

Analysis of Results: The resulting visualization (seen in Figure 12) plots the Timestamp (X-axis) against the Predicted Machine State (Y-axis). The graph clearly validates the model's accuracy in a real-world scenario, displaying a distinct "bump" or state change 1 that perfectly corresponds to the machine transitioning from an Idle state to a Cutting state and returning to Idle. 
