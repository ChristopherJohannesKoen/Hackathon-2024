import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
from collections import deque

class IsolationForestAnomalyDetector:
    def __init__(self, contamination=0.01):
        self.contamination = contamination  # Proportion of outliers in the data
        self.time_series_data = deque()  # To hold the time series data as it arrives
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
    
    def add_data(self, timestamp, value):
        """
        Adds a new data point to the time series.

        :param timestamp: The timestamp of the data point.
        :param value: The value of the data point.
        """
        self.time_series_data.append((timestamp, value))
    
    def detect_anomalies(self):
        """
        Applies the Isolation Forest algorithm to detect anomalies in the time series data.
        
        :return: The detected anomalies and the corresponding anomaly scores.
        """
        if not self.time_series_data:
            raise ValueError("No data available for anomaly detection.")
        
        timestamps, values = zip(*self.time_series_data)
        values = np.array(values).reshape(-1, 1)  # Reshape data for Isolation Forest
        
        # Fit the Isolation Forest model
        self.model.fit(values)
        
        # Predict anomalies (-1 for anomaly, 1 for normal)
        predictions = self.model.predict(values)
        
        # Anomaly score (the lower, the more abnormal)
        anomaly_scores = self.model.decision_function(values)
        
        # Detect anomalies
        anomalies = [(timestamp, value) for timestamp, value, prediction in zip(timestamps, values, predictions) if prediction == -1]
        return anomalies, anomaly_scores
    
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
        Clears the stored time series data.
        """
        self.time_series_data.clear()

if __name__ == "__main__":
    # Example of how to use the IsolationForestAnomalyDetector with a simulated data stream
    detector = IsolationForestAnomalyDetector(contamination=0.01)
    
    # Simulate a data stream
    current_time = datetime.now()
    for i in range(1000):
        timestamp = current_time + timedelta(minutes=i)
        value = np.random.normal(loc=100, scale=5)  # Simulate some data
        detector.add_data(timestamp, value)
        
        # Simulate anomaly by adding a large value
        if i % 200 == 0:
            anomaly_value = np.random.normal(loc=150, scale=5)
            detector.add_data(timestamp, anomaly_value)

        # Periodically check for anomalies
        if i % 100 == 0 and i > 0:
            anomalies, scores = detector.detect_anomalies()
            if anomalies:
                print(f"Anomalies detected: {anomalies}")
                detector.visualize_anomalies(anomalies)
            else:
                print("No anomalies detected.")

    # Clear the data after processing
    detector.clear_data()
