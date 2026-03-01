import json
import os
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np

class SyntheticLabelPATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False, threshold=None, result=None, labels=None):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.threshold = threshold  # To store the calculated threshold
        self.result = result  # To store the PATE score
        self.labels = labels if labels is not None else []  # To store the anomaly labels

    def detect_single_anomaly(self, value):
        """
        Detect if a single new data point is an anomaly using the stored threshold.
        """
        if value > self.threshold:
            print(f"Anomaly detected for value {value}")
            return 1  # Anomaly
        else:
            return 0  # Normal

    def update_model_attributes(self, value):
        """
        Update the model attributes after processing a new data point.
        """
        # Update threshold (example: adjust based on new value)
        self.threshold = np.mean(self.labels) + 2 * np.std(self.labels)
        print(f"Updated threshold: {self.threshold}")

def get_service_name(id):
    with open('id.json', 'r') as f:
        id_mapping = json.load(f)
    return id_mapping.get(id)

def access_service_folder(service_name):
    service_folder_path = f"./{service_name}"
    if os.path.exists(service_folder_path):
        return service_folder_path
    else:
        raise FileNotFoundError(f"Service folder for {service_name} not found.")

def load_attributes(service_folder_path):
    attributes_file_path = os.path.join(service_folder_path, 'pateIsoTree4V1PointAttributes.txt')
    attributes = {}
    with open(attributes_file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            if key == 'Anomaly Labels':
                attributes[key] = [int(x) for x in value.strip('[]').split(',')]
            elif value.lower() in ['true', 'false']:  # Handle boolean values
                attributes[key] = value.lower() == 'true'
            else:
                attributes[key] = float(value) if '.' in value else int(value)
    return attributes

def save_attributes(service_folder_path, detector):
    attributes_file_path = os.path.join(service_folder_path, 'pateIsoTree4V1PointAttributes.txt')
    with open(attributes_file_path, 'w') as f:
        f.write(f"e_buffer={detector.e_buffer}\n")
        f.write(f"d_buffer={detector.d_buffer}\n")
        f.write(f"binary_scores={detector.binary_scores}\n")
        f.write(f"threshold={detector.threshold}\n")
        f.write(f"PATE Score (AUC-PR)={detector.result}\n")
        f.write(f"Anomaly Labels={detector.labels}\n")
    print(f"Attributes saved to {attributes_file_path}")

def append_data_to_csv(service_folder_path, timestamp, value, is_anomaly):
    data_csv_path = os.path.join(service_folder_path, 'pateIsoTree4V1PointProcessedData.csv')
    if os.path.exists(data_csv_path):
        df = pd.read_csv(data_csv_path)
    else:
        # Create a new DataFrame if the file does not exist
        df = pd.DataFrame(columns=['reference_time', 'is_anomaly', 'usage_end_time', 'cost', 'usage_amount', 'usage_unit', 'service_type'])

    # Clean the usage_end_time column to ensure correct datetime format
    df['usage_end_time'] = df['usage_end_time'].str.split('.').str[0]
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

    # Drop any rows where the conversion failed (NaT values)
    df = df.dropna(subset=['usage_end_time'])

    new_entry = pd.DataFrame([{
        'reference_time': (timestamp - df['usage_end_time'].min()).total_seconds() / 3600 if not df.empty else 0,
        'is_anomaly': is_anomaly,
        'usage_end_time': timestamp,
        'cost': value,
        'usage_amount': None,  # Update if necessary
        'usage_unit': None,  # Update if necessary
        'service_type': None  # Update if necessary
    }])

    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(data_csv_path, index=False)
    print(f"New data appended and saved to {data_csv_path}")

def get_service_name(id):
    with open('ids.json', 'r') as f:
        id_mapping = json.load(f)
    return id_mapping.get(id)

def access_service_folder(service_name):
    service_folder_path = f"./runTimeData/{service_name}"
    if os.path.exists(service_folder_path):
        return service_folder_path
    else:
        raise FileNotFoundError(f"Service folder for {service_name} not found.")

def extract_last_96_hours(service_folder_path):
    processed_csv_path = os.path.join(service_folder_path, 'pateIsoTree4V1PointProcessedData.csv')
    df_processed = pd.read_csv(processed_csv_path)
    
    # Clean the usage_end_time column to ensure correct datetime format
    df_processed['usage_end_time'] = df_processed['usage_end_time'].str.split('.').str[0]
    df_processed['usage_end_time'] = pd.to_datetime(df_processed['usage_end_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    # Drop any rows where the conversion failed (NaT values)
    df_processed = df_processed.dropna(subset=['usage_end_time'])
    
    # Sort by usage_end_time and select the last 96 hours
    df_sorted = df_processed.sort_values(by='usage_end_time', ascending=False)
    last_96_hours = df_sorted.head(96)
    
    time_location_array = last_96_hours['reference_time'].tolist()
    anomaly_array = last_96_hours['is_anomaly'].tolist()
    
    output_json = {
        "relative_time_locations": time_location_array,
        "anomalies": anomaly_array
    }
    
    json_output_path = os.path.join(service_folder_path, 'pateIsoTree4V1Point_last_96_hours_anomalies.json')
    with open(json_output_path, 'w') as json_file:
        json.dump(output_json, json_file)
    
    print(f"JSON file saved to {json_output_path}")

def UpdateFile(received_id, value):
    # Step 1: Get service name and folder path
    service_name = get_service_name(received_id)
    service_folder_path = access_service_folder(service_name)

    # Step 2: Load existing attributes
    attrs = load_attributes(service_folder_path)

    # Initialize the detector with the loaded attributes
    detector = SyntheticLabelPATEAnomalyDetector(
        e_buffer=attrs['e_buffer'],
        d_buffer=attrs['d_buffer'],
        binary_scores=bool(attrs['binary_scores']),
        threshold=attrs['threshold'],
        result=attrs['PATE Score (AUC-PR)'],
        labels=attrs['Anomaly Labels']
    )

    # Step 3: Detect if the new value is an anomaly
    is_anomaly = detector.detect_single_anomaly(value)

    # Step 4: Update the model's attributes with the new data point
    detector.labels.append(is_anomaly)
    detector.update_model_attributes(value)

    # Step 5: Append the new data to the CSV
    timestamp = pd.Timestamp.now()  # Assume current timestamp for the new data point
    append_data_to_csv(service_folder_path, timestamp, value, is_anomaly)

    # Step 6: Save the updated attributes to the .txt file
    save_attributes(service_folder_path, detector)

    # Step 2-3: Access the service folder
    service_name = get_service_name(received_id)
    service_folder_path = access_service_folder(service_name)

    # Step 7: Extract the last 96 hours and generate JSON
    extract_last_96_hours(service_folder_path)



