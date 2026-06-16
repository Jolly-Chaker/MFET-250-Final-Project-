# Data Preparation and Preprocessing 

With the database successfully aggregating data from both the CNC machine and the microphone sensor, the first phase of development involved preparing this dataset for training. 

  - Data Export & Cleaning: We exported the raw sensor data into a CSV format. Leveraging AI-assisted coding, we developed a preprocessing script to clean the data, specifically targeting and removing noise to ensure high data quality.
  
  - Dataset Creation: This cleaned historical data served as our ground truth training dataset, labeled with the corresponding machine states (Idle, Cutting, etc.). 

# Model Training and Optimization 

  - Cloud-Optimized Architecture: A key consideration during the coding phase was the deployment environment. We used minimal, low-storage Python libraries to ensure the model remained lightweight. This optimization was crucial to ensuring the code could execute efficiently within the storage and memory constraints of a cloud environment such as AWS Lambda. 

  - Performance Validation: The model was trained and rigorously validated against a test set. We achieved a high classification accuracy of **96%**. To further analyze performance, we generated a Confusion Matrix, which provided a detailed breakdown of the model's precision across different machine states. 
