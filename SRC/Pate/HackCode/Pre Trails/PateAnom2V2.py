import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pate.PATE_metric import PATE
from datetime import datetime

class PATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False, rolling_window=100):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.rolling_window = rolling_window

    def detect_anomalies(self, timestamps, values, labels=None):
        """
        Applies the PATE algorithm to detect anomalies in the time series data.
        
        :param timestamps: List of timestamps.
        :param values: List of corresponding values.
        :param labels: Optional ground truth labels for supervised anomaly detection.
        :return: The PATE score (AUC-PR) and any detected anomalies.
        """
        y_score = np.array(values)
        
        # Apply the PATE algorithm if ground truth labels are provided
        if labels is not None:
            y_true = np.array(labels)
            result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
            print("PATE Score (AUC-PR):", result)
        else:
            print("No ground truth labels provided. Running unsupervised anomaly detection.")
            result = None

        # Detect anomalies using an adaptive threshold
        anomalies = self._detect_anomalies(timestamps, values, y_score)
        return result, anomalies

    def _detect_anomalies(self, timestamps, values, y_score):
        """
        Detects anomalies using a rolling window for an adaptive threshold.
        
        :param timestamps: List of timestamps.
        :param values: List of corresponding values.
        :param y_score: The predicted scores for each data point.
        :return: A list of anomalies.
        """
        anomalies = []
        for i in range(len(y_score)):
            if i < self.rolling_window:
                # Use a static threshold for the initial points
                threshold = np.mean(y_score[:i+1]) + 2 * np.std(y_score[:i+1])
            else:
                # Use a rolling threshold for the rest
                threshold = np.mean(y_score[i-self.rolling_window:i+1]) + 2 * np.std(y_score[i-self.rolling_window:i+1])
            
            if y_score[i] > threshold:
                anomalies.append((timestamps[i], values[i]))

        return anomalies
    
    def visualize_anomalies(self, timestamps, values, anomalies):
        """
        Visualizes the time series data and highlights the detected anomalies.

        :param timestamps: List of timestamps.
        :param values: List of corresponding values.
        :param anomalies: A list of detected anomalies.
        """
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

if __name__ == "__main__":
    # Load data from CSV
    df = pd.read_csv("C:/Users/<redacted-user>/Documents/Hackathon 2024/Hackathon2024/SRC/Data/split_data/Compute Engine.csv")
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

    # Prepare data
    timestamps = df['usage_end_time'].tolist()
    values = df['cost'].tolist()

    # Initialize the PATE anomaly detector
    detector = PATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False, rolling_window=100)
    
    # Detect anomalies
    score, anomalies = detector.detect_anomalies(timestamps, values)

    if anomalies:
        print(f"Anomalies detected: {anomalies}")
    else:
        print("No anomalies detected.")

    # Visualize the detected anomalies
    detector.visualize_anomalies(timestamps, values, anomalies)
