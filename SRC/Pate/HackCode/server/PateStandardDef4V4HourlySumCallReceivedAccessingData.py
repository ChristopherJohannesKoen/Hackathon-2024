import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from pate.PATE_metric import PATE  # Ensure the PATE_metric module is correctly installed and accessible

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

def read_data_csv(service_folder_path):
    data_csv_path = os.path.join(service_folder_path, 'data.csv')
    if os.path.exists(data_csv_path):
        df = pd.read_csv(data_csv_path)
        df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])
        return df
    else:
        raise FileNotFoundError(f"Data.csv file not found in {service_folder_path}.")

def run_model(service_folder_path):
    class SyntheticLabelPATEAnomalyDetector:
        def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False):
            self.e_buffer = e_buffer
            self.d_buffer = d_buffer
            self.binary_scores = binary_scores
            self.threshold = None
            self.result = None
            self.labels = None

        def preprocess_data(self, df):
            print("Starting preprocessing of data to calculate hourly sums...")
            df.set_index('usage_end_time', inplace=True)

            numeric_columns = df.select_dtypes(include=[np.number]).columns
            df_resampled = df[numeric_columns].resample('H').sum()

            df_non_numeric = df[['usage_unit', 'service_type']].resample('H').first()

            df_resampled = df_resampled.join(df_non_numeric).reset_index()

            print(f"Hourly sums calculated:\n{df_resampled.head()}")
            return df_resampled

        def generate_synthetic_labels(self, values):
            print("Starting synthetic label generation using Isolation Forest...")
            model = IsolationForest(contamination=0.01, random_state=42)
            model.fit(np.array(values).reshape(-1, 1))
            labels = model.predict(np.array(values).reshape(-1, 1))
            labels = np.where(labels == -1, 1, 0)

            print(f"Synthetic labels generated: {labels}")
            return labels

        def detect_anomalies(self, timestamps, values):
            print("Starting anomaly detection process...")
            self.labels = self.generate_synthetic_labels(values)

            y_score = np.array(values)
            y_true = np.array(self.labels)

            print("Running the PATE algorithm...")
            self.result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
            print(f"PATE Score (AUC-PR): {self.result}")

            anomalies = self._detect_anomalies(timestamps, values, y_score)
            print(f"Anomalies detected: {anomalies}")

            return self.result, anomalies, self.labels

        def _detect_anomalies(self, timestamps, values, y_score):
            print("Calculating threshold for anomaly detection...")
            self.threshold = np.mean(y_score) + 2 * np.std(y_score)
            print(f"Calculated threshold: {self.threshold}")

            anomalies = [(timestamps[i], values[i]) for i in range(len(y_score)) if y_score[i] > self.threshold]
            return anomalies

        def visualize_anomalies(self, timestamps, values, anomalies):
            print("Visualizing anomalies...")

            plt.figure(figsize=(14, 7))
            plt.plot(timestamps, values, label='Time Series Data')

            if anomalies:
                anomaly_timestamps, anomaly_values = zip(*anomalies)
                plt.scatter(anomaly_timestamps, anomaly_values, color='red', label='Detected Anomalies')

            plt.title('Time Series Data with Detected Anomalies')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.legend()
            plt.grid(True)
            plt.show()

            print("Visualization complete.")

        def save_attributes(self, filepath):
            with open(filepath, 'w') as f:
                f.write(f"e_buffer={self.e_buffer}\n")
                f.write(f"d_buffer={self.d_buffer}\n")
                f.write(f"binary_scores={self.binary_scores}\n")
                f.write(f"threshold={self.threshold}\n")
                f.write(f"PATE Score (AUC-PR)={self.result}\n")
                f.write(f"Anomaly Labels={self.labels.tolist()}\n")

    print(f"Running model for service folder path: {service_folder_path}")

    csv_file_path = os.path.join(service_folder_path, 'data.csv')
    df = pd.read_csv(csv_file_path)
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

    print("Data loaded successfully.")

    detector = SyntheticLabelPATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False)

    df_resampled = detector.preprocess_data(df)

    timestamps = df_resampled['usage_end_time'].tolist()
    values = df_resampled['cost'].tolist()
    score, anomalies, labels = detector.detect_anomalies(timestamps, values)

    df_resampled['is_anomaly'] = labels
    df_resampled['reference_time'] = (df_resampled['usage_end_time'] - df_resampled['usage_end_time'].min()).dt.total_seconds() / 3600

    df_output = df_resampled[['reference_time', 'is_anomaly', 'usage_end_time', 'cost', 'usage_amount', 'usage_unit', 'service_type']]

    processed_data_path = os.path.join(service_folder_path, 'pateStandardDef4V4HourlySumProcessedData.csv')
    df_output.to_csv(processed_data_path, index=False)
    print(f"Processed data saved to {processed_data_path}")

    attributes_path = os.path.join(service_folder_path, 'pateStandardDef4V4HourlyAttributes.txt')
    detector.save_attributes(attributes_path)
    print(f"Attributes saved to {attributes_path}")

    detector.visualize_anomalies(timestamps, values, anomalies)

    print("Process completed.")

def CRADRM(received_id):
    print(f"Starting CRADRM for received_id: {received_id}")

    service_name = get_service_name(received_id)
    print(f"Service name retrieved: {service_name}")

    try:
        service_folder_path = access_service_folder(service_name)
        print(f"Service folder path accessed: {service_folder_path}")
    except FileNotFoundError as e:
        print(f"Error accessing service folder path: {e}")
        return

    try:
        df = read_data_csv(service_folder_path)
        print(f"Data.csv read successfully. First few rows:\n{df.head()}")
    except FileNotFoundError as e:
        print(f"Error reading Data.csv: {e}")
        return

    try:
        run_model(service_folder_path)
        print("Model run successfully.")
    except Exception as e:
        print(f"Error running the model: {e}")

    print("CRADRM process completed.")
