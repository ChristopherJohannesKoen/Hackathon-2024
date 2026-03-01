import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from datetime import datetime
from collections import deque
from pate.PATE_metric import PATE
from sklearn.preprocessing import MinMaxScaler

class IsolationForestAnomalyDetector:
    def __init__(self, contamination=0.01, window_size=100):
        self.contamination = contamination  # Proportion of outliers in the data
        self.time_series_data = deque(maxlen=window_size)  # Rolling window for time series data
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
        self.scaler = MinMaxScaler()  # Normalize the data
        
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
        
        # Normalize values
        scaled_values = self.scaler.fit_transform(values)
        
        # Fit the Isolation Forest model
        self.model.fit(scaled_values)
        
        # Predict anomalies (-1 for anomaly, 1 for normal)
        predictions = self.model.predict(scaled_values)
        
        # Anomaly score (the lower, the more abnormal)
        anomaly_scores = self.model.decision_function(scaled_values)
        
        # Detect anomalies
        anomalies = [(timestamp, value) for timestamp, value, prediction in zip(timestamps, values.flatten(), predictions) if prediction == -1]
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

class PATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False, window_size=100):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.time_series_data = deque(maxlen=window_size)  # Rolling window for time series data
        self.labels = deque(maxlen=window_size)  # Rolling window for ground truth labels

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

        # Detect anomalies
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

class CombinedAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False, contamination=0.01, window_size=100):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.contamination = contamination
        self.time_series_data = deque(maxlen=window_size)  # Rolling window for time series data
        self.labels = deque(maxlen=window_size)  # Rolling window for ground truth labels
        
        # Initialize models
        self.isolation_forest = IsolationForest(contamination=self.contamination, random_state=42)
        self.pate_result = None
        self.isolation_forest_result = None
        self.scaler = MinMaxScaler()  # Normalize the data

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
    
    def run_pate(self):
        """
        Runs the PATE algorithm on the current time series data.
        
        :return: The PATE score (AUC-PR) and detected anomalies.
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
            self.pate_result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
            print("PATE Score (AUC-PR):", self.pate_result)
        else:
            print("Ground truth labels (y_true) not provided. Consider applying an anomaly detection model to generate y_true labels.")
            self.pate_result = None

        # Detect anomalies using PATE (same method as before)
        anomalies = self._detect_anomalies(y_score)
        return self.pate_result, anomalies
    
    def run_isolation_forest(self):
        """
        Runs the Isolation Forest algorithm on the current time series data.
        
        :return: The detected anomalies and the corresponding anomaly scores.
        """
        if not self.time_series_data:
            raise ValueError("No data available for anomaly detection.")
        
        timestamps, values = zip(*self.time_series_data)
        values = np.array(values).reshape(-1, 1)  # Reshape data for Isolation Forest
        
        # Normalize values
        scaled_values = self.scaler.fit_transform(values)
        
        # Fit the Isolation Forest model
        self.isolation_forest.fit(scaled_values)
        
        # Predict anomalies (-1 for anomaly, 1 for normal)
        predictions = self.isolation_forest.predict(scaled_values)
        
        # Anomaly score (the lower, the more abnormal)
        anomaly_scores = self.isolation_forest.decision_function(scaled_values)
        
        # Detect anomalies
        anomalies = [(timestamp, value) for timestamp, value, prediction in zip(timestamps, values.flatten(), predictions) if prediction == -1]
        return anomalies, anomaly_scores
    
    def _detect_anomalies(self, y_score):
        """
        Detects anomalies based on a simple threshold.
        
        :param y_score: The predicted scores for each data point.
        :return: A list of anomalies.
        """
        threshold = np.mean(y_score) + 2 * np.std(y_score)  # Example threshold
        anomalies = [(timestamp, value) for timestamp, value in zip(self.time_series_data, y_score) if value > threshold]
        return anomalies
    
    def compare_models(self):
        """
        Compares the performance of PATE and Isolation Forest based on a chosen strategy.
        
        :return: A dictionary with the comparison results and the chosen model.
        """
        comparison_results = {
            'PATE': self.pate_result,
            'IsolationForest': None,  # We'll update this after running Isolation Forest
            'ChosenModel': None
        }

        # Run Isolation Forest and get the anomaly scores
        anomalies, isolation_forest_scores = self.run_isolation_forest()
        
        # Simple comparison strategy: choose the model with more anomalies detected
        if self.pate_result is not None:
            comparison_results['IsolationForest'] = len(anomalies)
            comparison_results['ChosenModel'] = 'PATE' if self.pate_result > len(anomalies) else 'IsolationForest'
        else:
            comparison_results['IsolationForest'] = len(anomalies)
            comparison_results['ChosenModel'] = 'IsolationForest'

        return comparison_results
    
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
    # Example of how to use the CombinedAnomalyDetector with real data from a CSV file
    detector = CombinedAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False, contamination=0.01)
    
    # Load data from CSV
    df = pd.read_csv("C:/Users/<redacted-user>/Documents/Hackathon 2024/Hackathon2024/SRC/Data/split_data/Compute Engine.csv")
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

    for index, row in df.iterrows():
        timestamp = row['usage_end_time']
        value = row['cost']
        detector.add_data(timestamp, value)
        
    # After all data is added, run the anomaly detection and visualization
    print("Running PATE...")
    pate_score, pate_anomalies = detector.run_pate()
    print("Running Isolation Forest...")
    isolation_forest_anomalies, isolation_forest_scores = detector.run_isolation_forest()
    comparison_results = detector.compare_models()

    print(f"Comparison Results: {comparison_results}")

    # Visualize the combined results in a single plot
    if pate_anomalies or isolation_forest_anomalies:  # Ensure that there are anomalies to plot
        detector.visualize_anomalies(pate_anomalies if comparison_results['ChosenModel'] == 'PATE' else isolation_forest_anomalies)
    else:
        print("No anomalies detected by either model.")

    # Clear the data after processing
    detector.clear_data()
