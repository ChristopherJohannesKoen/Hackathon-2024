import json
import os
import pandas as pd
from datetime import timedelta

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

def extract_last_96_hours(service_folder_path):
    processed_csv_path = os.path.join(service_folder_path, 'pateStandardDef4V1PointProcessedData.csv')
    df_processed = pd.read_csv(processed_csv_path)
    
    # Sort by usage_end_time and select the last 96 hours
    df_processed['usage_end_time'] = pd.to_datetime(df_processed['usage_end_time'])
    df_sorted = df_processed.sort_values(by='usage_end_time', ascending=False)
    
    last_96_hours = df_sorted.head(96)
    
    time_location_array = last_96_hours['reference_time'].tolist()
    anomaly_array = last_96_hours['is_anomaly'].tolist()
    
    output_json = {
        "relative_time_locations": time_location_array,
        "anomalies": anomaly_array
    }
    
    json_output_path = os.path.join(service_folder_path, 'pateStandardDef4V1Point_last_96_hours_anomalies.json')
    with open(json_output_path, 'w') as json_file:
        json.dump(output_json, json_file)
    
    print(f"JSON file saved to {json_output_path}")


#ExtractLast96Hours = EL96H
def EL96H(received_id):

    # Step 2-3: Access the service folder
    service_name = get_service_name(received_id)
    service_folder_path = access_service_folder(service_name)

    # Step 7: Extract the last 96 hours and generate JSON
    extract_last_96_hours(service_folder_path)
