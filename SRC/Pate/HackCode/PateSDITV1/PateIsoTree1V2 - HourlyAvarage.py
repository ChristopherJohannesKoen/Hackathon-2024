import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from pate.PATE_metric import PATE
from datetime import datetime, timedelta
from collections import deque

class PATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.time_series_data = deque()  # To hold the time series data as it arrives
        self.labels = deque()  # To hold dynamic ground truth labels

    def preprocess_data(self, df):
        """
        Preprocesses the data to calculate the hourly averages.
        
        :param df: DataFrame containing the raw data with timestamps and values.
        :return: Lists of timestamps and their corresponding average values.
        """
        print("Starting preprocessing of data to calculate hourly averages...")

        # Ensure 'usage_end_time' is the index
        df.set_index('usage_end_time', inplace=True)

        # Calculate hourly averages
        df_resampled = df.resample('H').mean().reset_index()

        print(f"Hourly averages calculated:\n{df_resampled.head()}")
        return df_resampled['usage_end_time'].tolist(), df_resampled['cost'].tolist()

    def add_data(self, timestamp, value):
        """
        Adds a new data point to the time series and updates the dynamic ground truth labels.

        :param timestamp: The timestamp of the data point.
        :param value: The value of the data point.
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
        
        :return: The PATE score (AUC-PR) and any detected anomalies.
        """
        if not self.time_series_data:
            raise ValueError("No data available for anomaly detection.")
        
        timestamps, values = zip(*self.time_series_data)
        y_score = np.array(values)
        
        # Check if labels are available
        if self.labels:
            y_true = np.array(self.labels)
            print("Running PATE algorithm...")
            result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
            print("PATE Score (AUC-PR):", result)
        else:
            print("No ground truth labels available.")
            result = None

        # Detect anomalies and return them along with the PATE score
        anomalies = self._detect_anomalies(y_score)
        return result, anomalies

    def _detect_anomalies(self, y_score):
        """
        Detects anomalies based on the PATE score.
        
        :param y_score: The predicted scores for each data point.
        :return: A list of anomalies.
        """
        print("Detecting anomalies...")
        threshold = np.mean(y_score) + 2 * np.std(y_score)
        print(f"Anomaly detection threshold: {threshold}")
        anomalies = [(timestamp, value) for (timestamp, value), score in zip(self.time_series_data, y_score) if score > threshold]
        print(f"Anomalies detected: {anomalies}")
        return anomalies
    
    def visualize_anomalies(self, anomalies):
        """
        Visualizes the time series data and highlights the detected anomalies.
        
        :param anomalies: A list of detected anomalies.
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

    def clear_data(self):
        """
        Clears the stored time series data and labels.
        """
        print("Clearing all stored data and labels...")
        self.time_series_data.clear()
        self.labels.clear()

if __name__ == "__main__":
    # Load data from CSV
    df = pd.read_csv("./SRC/Data/split_data/Cloud Storage TEST DO NOT USE.csv")
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

    # Initialize the PATE anomaly detector
    detector = PATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False)

    # Preprocess data to calculate hourly averages
    timestamps, values = detector.preprocess_data(df)

    # Add data points to the detector
    for timestamp, value in zip(timestamps, values):
        detector.add_data(timestamp, value)

    # Detect anomalies
    score, anomalies = detector.detect_anomalies()

    if anomalies:
        print(f"Anomalies detected: {anomalies}")
    else:
        print("No anomalies detected.")

    # Visualize the detected anomalies
    detector.visualize_anomalies(anomalies)
