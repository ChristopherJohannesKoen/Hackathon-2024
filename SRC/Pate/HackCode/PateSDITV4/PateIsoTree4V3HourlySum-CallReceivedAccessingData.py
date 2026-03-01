import json
import os
import pandas as pd
from subprocess import run

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

def read_data_csv(service_folder_path):
    data_csv_path = os.path.join(service_folder_path, 'Data.csv')
    if os.path.exists(data_csv_path):
        df = pd.read_csv(data_csv_path)
        df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])
        return df
    else:
        raise FileNotFoundError("Data.csv file not found.")
    
def run_model(service_folder_path):
    # Assuming the model script is in the same directory and takes the service folder path as an argument
    model_script = os.path.join(service_folder_path, 'PateIsoTree4V3 - HourlySum.py')
    if os.path.exists(model_script):
        run(["python", model_script], check=True)
    else:
        raise FileNotFoundError(f"Model script not found in {service_folder_path}")


#CallReceivedAccessingDataRunModel = CRADRM
def CRADRM(received_id):

    # Step 2-3: Access the service folder
    service_name = get_service_name(received_id)
    service_folder_path = access_service_folder(service_name)

    # Step 4: Read Data.csv
    df = read_data_csv(service_folder_path)

    # Step 5: Run the model
    run_model(service_folder_path)
