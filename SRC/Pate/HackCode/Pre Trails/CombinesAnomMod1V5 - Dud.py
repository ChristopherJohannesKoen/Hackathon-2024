import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
from collections import deque
from pate.PATE_metric import PATE
from sklearn.preprocessing import MinMaxScaler

class IsolationForestAnomalyDetector:
    def __init__(self, contamination=0.01):
        self.contamination = contamination  # Proportion of outliers in the data
        self.time_series_data = deque()  # To hold the time series data as it arrives
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
    
    def add_data(self, timestamp, value):
        self.time_series_data.append((timestamp, value))
    
    def detect_anomalies(self):
        if not self.time_series_data:
            raise ValueError("No data available for anomaly detection.")
        
        timestamps, values = zip(*self.time_series_data)
        values = np.array(values).reshape(-1, 1)  # Reshape data for Isolation Forest
        
        self.model.fit(values)
        predictions = self.model.predict(values)
        anomaly_scores = self.model.decision_function(values)
        anomalies = [(timestamp, value) for timestamp, value, prediction in zip(timestamps, values.flatten(), predictions) if prediction == -1]
        return anomalies, anomaly_scores
    
    def clear_data(self):
        self.time_series_data.clear()

class PATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.time_series_data = deque()  
        self.labels = deque()  

    def add_data(self, timestamp, value, label=None):
        self.time_series_data.append((timestamp, value))
        if label is not None:
            self.labels.append(label)
    
    def detect_anomalies(self):
        if not self.time_series_data:
            raise ValueError("No data available for anomaly detection.")
        
        timestamps, values = zip(*self.time_series_data)
        y_score = np.array(values)
        
        if self.labels:
            y_true = np.array(self.labels)
        else:
            y_true = None

        if y_true is not None:
            result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
            print("PATE Score (AUC-PR):", result)
        else:
            print("Ground truth labels (y_true) not provided. Consider applying an anomaly detection model to generate y_true labels.")
            result = None

        anomalies = self._detect_anomalies(y_score)
        return result, anomalies

    def _detect_anomalies(self, y_score):
        threshold = np.mean(y_score) + 2 * np.std(y_score)
        anomalies = [(timestamp, value) for (timestamp, value), score in zip(self.time_series_data, y_score) if score > threshold]
        return anomalies
    
    def clear_data(self):
        self.time_series_data.clear()
        self.labels.clear()

class CombinedAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False, contamination=0.01):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.contamination = contamination
        self.time_series_data = deque()  # To hold the time series data as it arrives
        self.labels = deque()  # To hold ground truth labels if available
        
        # Initialize models
        self.isolation_forest = IsolationForest(contamination=self.contamination, random_state=42)
        self.pate_result = None
        self.isolation_forest_result = None
        self.scaler = MinMaxScaler()

    def add_data(self, timestamp, value, label=None):
        self.time_series_data.append((timestamp, value))
        if label is not None:
            self.labels.append(label)
    
    def run_pate(self):
        if not self.time_series_data:
            raise ValueError("No data available for anomaly detection.")
        
        timestamps, values = zip(*self.time_series_data)
        y_score = np.array(values)
        
        if self.labels:
            y_true = np.array(self.labels)
        else:
            y_true = None

        if y_true is not None:
            self.pate_result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
            print("PATE Score (AUC-PR):", self.pate_result)
        else:
            print("Ground truth labels (y_true) not provided. Consider applying an anomaly detection model to generate y_true labels.")
            self.pate_result = None

        anomalies = self._detect_anomalies(y_score)
        return self.pate_result, anomalies
    
    def run_isolation_forest(self):
        if not self.time_series_data:
            raise ValueError("No data available for anomaly detection.")
        
        timestamps, values = zip(*self.time_series_data)
        values = np.array(values).reshape(-1, 1)  # Reshape data for Isolation Forest

        scaled_values = self.scaler.fit_transform(values)

        self.isolation_forest.fit(scaled_values)
        predictions = self.isolation_forest.predict(scaled_values)
        anomaly_scores = self.isolation_forest.decision_function(scaled_values)
        anomalies = [(timestamp, value) for timestamp, value, prediction in zip(timestamps, values.flatten(), predictions) if prediction == -1]
        return anomalies, anomaly_scores
    
    def _detect_anomalies(self, y_score):
        threshold = np.mean(y_score) + 2 * np.std(y_score)  # Example threshold
        anomalies = [(timestamp, value) for timestamp, value in zip(self.time_series_data, y_score) if value > threshold]
        return anomalies

    def compare_models(self):
        comparison_results = {
            'PATE': self.pate_result,
            'IsolationForest': None,
            'ChosenModel': None
        }

        anomalies, isolation_forest_scores = self.run_isolation_forest()
        
        if self.pate_result is not None:
            comparison_results['IsolationForest'] = len(anomalies)
            comparison_results['ChosenModel'] = 'PATE' if self.pate_result > len(anomalies) else 'IsolationForest'
        else:
            comparison_results['IsolationForest'] = len(anomalies)
            comparison_results['ChosenModel'] = 'IsolationForest'

        return comparison_results
    
    def visualize_combined_anomalies(self, pate_anomalies, isolation_forest_anomalies):
        if not self.time_series_data:
            raise ValueError("No data available for visualization.")

        timestamps, values = zip(*self.time_series_data)

        # Debug: Ensure that anomalies are correctly detected
        print(f"PATE Anomalies: {pate_anomalies}")
        print(f"Isolation Forest Anomalies: {isolation_forest_anomalies}")

        plt.figure(figsize=(14, 7))
        plt.plot(timestamps, values, label='Time Series Data')

        if pate_anomalies:
            pate_timestamps, pate_values = zip(*pate_anomalies)
            plt.scatter(pate_timestamps, pate_values, color='red', label='PATE Detected Anomalies')

        if isolation_forest_anomalies:
            isolation_forest_timestamps, isolation_forest_values = zip(*isolation_forest_anomalies)
            plt.scatter(isolation_forest_timestamps, isolation_forest_values, color='blue', label='Isolation Forest Detected Anomalies')

        plt.title('Time Series Data with Detected Anomalies')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.show()

    def clear_data(self):
        self.time_series_data.clear()
        self.labels.clear()

if __name__ == "__main__":
    # Example of how to use the CombinedAnomalyDetector with real data
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
        detector.visualize_combined_anomalies(pate_anomalies, isolation_forest_anomalies)
    else:
        print("No anomalies detected by either model.")

    # Clear the data after processing
    detector.clear_data()
