import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pate.PATE_metric import PATE
from datetime import datetime, timedelta
from collections import deque

class PATEDifferenceAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.time_series_data = deque()  # To hold the time series data as it arrives
        self.labels = deque()  # To hold ground truth labels if available

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
    
    def calculate_differences(self):
        """
        Calculates the differences between consecutive values in the time series.
        
        :return: A list of differences.
        """
        timestamps, values = zip(*self.time_series_data)
        differences = np.diff(values)  # Calculate differences between consecutive values
        return timestamps[1:], differences  # Return timestamps from the second element onward

    def detect_anomalies(self):
        """
        Applies the PATE algorithm to detect anomalies in the time series data based on differences.
        
        :return: The PATE score (AUC-PR) and any detected anomalies.
        """
        # Ensure we have enough data points
        if len(self.time_series_data) < 2:
            raise ValueError("Not enough data available for anomaly detection.")
        
        # Calculate the differences
        timestamps, differences = self.calculate_differences()
        y_score = np.array(differences)

        # Check if labels are available
        if self.labels:
            y_true = np.array(self.labels)[1:]  # Align labels with differences
        else:
            y_true = None

        # Apply the PATE algorithm
        if y_true is not None:
            result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
            print("PATE Score (AUC-PR):", result)
        else:
            print("Ground truth labels (y_true) not provided. Consider applying an anomaly detection model to generate y_true labels.")
            result = None  # Initialize result as None or some placeholder value

        # Detect anomalies and return them along with the PATE score
        anomalies = self._detect_anomalies(timestamps, y_score)
        return result, anomalies

    def _detect_anomalies(self, timestamps, y_score):
        """
        Detects anomalies based on the PATE score.

        :param y_score: The predicted scores for each data point.
        :return: A list of anomalies.
        """
        threshold = np.mean(y_score) + 2 * np.std(y_score)  # Example threshold
        anomalies = [(timestamps[i], y_score[i]) for i in range(len(y_score)) if y_score[i] > threshold]
        return anomalies
    
    def visualize_anomalies(self, anomalies):
        """
        Visualizes the time series data and highlights the detected anomalies.

        :param anomalies: A list of detected anomalies.
        """
        if not self.time_series_data:
            raise ValueError("No data available for visualization.")

        timestamps, values = zip(*self.time_series_data)
        diffs_timestamps, differences = self.calculate_differences()

        plt.figure(figsize=(14, 7))
        plt.plot(diffs_timestamps, differences, label='Differences in Time Series Data')
        
        if anomalies:
            anomaly_timestamps, anomaly_values = zip(*anomalies)
            plt.scatter(anomaly_timestamps, anomaly_values, color='red', label='Detected Anomalies')

        plt.title('Differences in Time Series Data with Detected Anomalies')
        plt.xlabel('Time')
        plt.ylabel('Difference in Value')
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
    # Load data from CSV
    df = pd.read_csv("./SRC/Data/split_data/Compute Engine.csv")
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

    # Prepare data
    timestamps = df['usage_end_time'].tolist()
    values = df['cost'].tolist()

    # Initialize the PATE anomaly detector with differences
    detector = PATEDifferenceAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False)

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
