import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pate.PATE_metric import PATE
from datetime import datetime
from collections import deque

class PATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.time_series_data = deque()  # To hold the time series data as it arrives
        self.labels = deque()  # To hold ground truth labels if available
        self.time_series_data = deque(maxlen=100)  # This would create a rolling window of 100 data points


    def add_data(self, timestamp, value, label=None):
        """
        Adds a new data point to the time series.

        :param timestamp: The timestamp of the data point.
        :param value: The value of the data point.
        :param label: The ground truth label for the data point (optional).
        """
        self.time_series_data.append((timestamp, value))
        if label is not None:
            self.labels.append(label)
    
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
        else:
            y_true = None

        # Apply the PATE algorithm
        if y_true is not None:
            result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
            print("PATE Score (AUC-PR):", result)
        else:
            print("Ground truth labels (y_true) not provided. Consider applying an anomaly detection model to generate y_true labels.")
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
        threshold = np.mean(y_score) + 2 * np.std(y_score)  # Example threshold
        anomalies = [(timestamp, value) for (timestamp, value), score in zip(self.time_series_data, y_score) if score > threshold]
        return anomalies
    
    def visualize_anomalies(self, anomalies):
        """
        Visualizes the time series data and highlights the detected anomalies.

        :param anomalies: A list of detected anomalies.
        """
        if not self.time_series_data:
            raise ValueError("No data available for visualization.")

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
        self.time_series_data.clear()
        self.labels.clear()

if __name__ == "__main__":
    # Example of how to use the PATEAnomalyDetector with your real data
    detector = PATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False)
    
    # Load data from CSV
    df = pd.read_csv("C:/Users/<redacted-user>/Documents/Hackathon 2024/Hackathon2024/SRC/Data/split_data/Compute Engine.csv")
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

    for index, row in df.iterrows():
        timestamp = row['usage_end_time']
        value = row['cost']
        detector.add_data(timestamp, value)

        # Periodically check for anomalies
        if index % 100 == 0 and index > 0:
            score, anomalies = detector.detect_anomalies()
            if anomalies:
                print(f"Anomalies detected: {anomalies}")
                detector.visualize_anomalies(anomalies)
            else:
                print("No anomalies detected.")

    # Clear the data after processing
    detector.clear_data()
