import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from pate.PATE_metric import PATE
from datetime import datetime, timedelta
from collections import deque
import os

class PATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.time_series_data = deque()  # To hold the time series data as it arrives
        self.labels = deque()  # To hold dynamic ground truth labels
        self.threshold = None  # To store the calculated threshold
        self.result = None  # To store the PATE score

    def add_data(self, timestamp, value):
        """
        Adds a new data point to the time series and updates the dynamic ground truth labels.
        """
        print(f"Adding data point - Timestamp: {timestamp}, Value: {value}")
        self.time_series_data.append((timestamp, value))
        self.update_labels()  # Update ground truth labels with the new data

    def update_labels(self):
        """
        Updates the ground truth labels using Isolation Forest as new data points are added.
        """
        if len(self.time_series_data) > 1:
            print("Updating labels...")
            _, values = zip(*self.time_series_data)
            values_array = np.array(values).reshape(-1, 1)

            # Use IsolationForest to generate synthetic labels
            model = IsolationForest(contamination=0.01, random_state=42)
            model.fit(values_array)
            labels = model.predict(values_array)

            # Convert the labels (-1 for anomaly, 1 for normal) to binary labels (1 for anomaly, 0 for normal)
            labels = np.where(labels == -1, 1, 0)

            # Update the labels deque
            self.labels = deque(labels, maxlen=len(values))
            print(f"Labels updated: {list(self.labels)}")

    def detect_anomalies(self):
        """
        Applies the PATE algorithm to detect anomalies in the time series data.
        """
        if not self.time_series_data:
            raise ValueError("No data available for anomaly detection.")
        
        timestamps, values = zip(*self.time_series_data)
        y_score = np.array(values)
        
        # Check if labels are available
        if self.labels:
            y_true = np.array(self.labels)
            print("Running PATE algorithm...")
            self.result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
            print("PATE Score (AUC-PR):", self.result)
        else:
            print("No ground truth labels available.")
            self.result = None

        # Detect anomalies and return them along with the PATE score
        anomalies = self._detect_anomalies(y_score)
        return self.result, anomalies

    def _detect_anomalies(self, y_score):
        """
        Detects anomalies based on the PATE score.
        """
        print("Detecting anomalies...")
        self.threshold = np.mean(y_score) + 2 * np.std(y_score)
        print(f"Anomaly detection threshold: {self.threshold}")
        anomalies = [(timestamp, value) for (timestamp, value), score in zip(self.time_series_data, y_score) if score > self.threshold]
        print(f"Anomalies detected: {anomalies}")
        return anomalies
    
    def visualize_anomalies(self, anomalies):
        """
        Visualizes the time series data and highlights the detected anomalies.
        """
        if not self.time_series_data:
            raise ValueError("No data available for visualization.")

        print("Visualizing anomalies...")
        timestamps, values = zip(*self.time_series_data)
        
        if anomalies:
            anomaly_timestamps, anomaly_values = zip(*anomalies)
        else:
            anomaly_timestamps, anomaly_values = [], []

        plt.figure(figsize=(14, 7))
        plt.plot(timestamps, values, label='Time Series Data')
        
        if anomalies:
            plt.scatter(anomaly_timestamps, anomaly_values, color='red', label='Detected Anomalies')

        plt.title('Time Series Data with Detected Anomalies')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.show()

    def save_attributes(self, filepath):
        """
        Save the attributes of the last run to a file.
        """
        with open(filepath, 'w') as f:
            f.write(f"e_buffer={self.e_buffer}\n")
            f.write(f"d_buffer={self.d_buffer}\n")
            f.write(f"binary_scores={self.binary_scores}\n")
            f.write(f"threshold={self.threshold}\n")
            f.write(f"PATE Score (AUC-PR)={self.result}\n")
            f.write(f"Anomaly Labels={list(self.labels)}\n")

if __name__ == "__main__":
    # Load data from CSV
    csv_file_path = "./SRC/Pate/HackCode/ServerInterfaceProto/[serviceName]/Data.csv"
    df = pd.read_csv(csv_file_path)
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

    # Prepare data
    timestamps = df['usage_end_time'].tolist()
    values = df['cost'].tolist()

    # Initialize the PATE anomaly detector
    detector = PATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False)

    # Add data points to the detector
    for timestamp, value in zip(timestamps, values):
        detector.add_data(timestamp, value)

    # Detect anomalies
    score, anomalies = detector.detect_anomalies()

    if anomalies:
        print(f"Anomalies detected: {anomalies}")
    else:
        print("No anomalies detected.")

    # Prepare data for output
    df['is_anomaly'] = list(detector.labels)
    df['reference_time'] = (df['usage_end_time'] - df['usage_end_time'].min()).dt.total_seconds() / 3600  # Reference time in hours
    
    # Select relevant columns and save to processedData.csv
    df_output = df[['reference_time', 'is_anomaly', 'usage_end_time', 'cost', 'usage_amount', 'usage_unit', 'service_type']]
    
    # Save processedData.csv in the same directory as the input CSV
    output_dir = os.path.dirname(csv_file_path)
    processed_data_path = os.path.join(output_dir, 'pateIsoTree4V1PointProcessedData.csv')
    df_output.to_csv(processed_data_path, index=False)
    print(f"Processed data saved to {processed_data_path}")

    # Save the attributes to a file in the same directory as the input CSV
    attributes_path = os.path.join(output_dir, 'pateIsoTree4V1PointAttributes.txt')
    detector.save_attributes(attributes_path)
    print(f"Attributes saved to {attributes_path}")

    # Visualize the detected anomalies
    detector.visualize_anomalies(anomalies)
    
    print("Process completed.")
