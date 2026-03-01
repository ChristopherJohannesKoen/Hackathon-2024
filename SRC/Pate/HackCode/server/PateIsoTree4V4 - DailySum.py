import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from pate.PATE_metric import PATE
from collections import deque
import os

class PATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False, window_size=96):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.window_size = window_size  # The rolling window size (96 hours)
        self.time_series_data = deque(maxlen=None)  # To hold the time series data as it arrives
        self.labels = deque(maxlen=None)  # To hold dynamic ground truth labels
        self.threshold = None  # To store the calculated threshold
        self.result = None  # To store the PATE score

    def preprocess_data(self, df):
        """
        Preprocesses the data to sum the values for each day.
        
        :param df: DataFrame containing the raw data with timestamps and values.
        :return: Lists of timestamps and their corresponding summed values.
        """
        print("Starting preprocessing of data to calculate daily sums...")

        # Ensure 'usage_end_time' is the index
        df.set_index('usage_end_time', inplace=True)

        # Sum values for each day
        df_resampled = df.resample('D').sum().reset_index()

        print(f"Daily sums calculated:\n{df_resampled.head()}")
        return df_resampled

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
            self.labels = deque(labels, maxlen=None)
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
        
        :param y_score: The predicted scores for each data point.
        :return: A list of anomalies.
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
        
        :param anomalies: A list of detected anomalies.
        """
        if not self.time_series_data:
            raise ValueError("No data available for visualization.")

        print("Visualizing anomalies...")
        timestamps, values = zip(*self.time_series_data)
        
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

    def save_attributes(self, filepath):
        """
        Save the attributes of the last run to a file, including anomaly labels.
        """
        with open(filepath, 'w') as f:
            f.write(f"e_buffer={self.e_buffer}\n")
            f.write(f"d_buffer={self.d_buffer}\n")
            f.write(f"binary_scores={self.binary_scores}\n")
            f.write(f"window_size={self.window_size}\n")
            f.write(f"threshold={self.threshold}\n")
            f.write(f"PATE Score (AUC-PR)={self.result}\n")
            f.write(f"Anomaly Labels={list(self.labels)}\n")

    def save_processed_data(self, df_resampled, output_dir):
        """
        Save the processed data with reference time and anomaly labels.
        """
        # Pad the labels with zeros at the beginning to match the length of df_resampled
        padded_labels = [0] * (len(df_resampled) - len(self.labels)) + list(self.labels)

        df_resampled['is_anomaly'] = padded_labels
        df_resampled['reference_time'] = (df_resampled['usage_end_time'] - df_resampled['usage_end_time'].min()).dt.total_seconds() / 3600  # Reference time in hours
        
        # Select relevant columns and save to processedData.csv
        df_output = df_resampled[['reference_time', 'is_anomaly', 'usage_end_time', 'cost', 'usage_amount', 'usage_unit', 'service_type']]
        
        processed_data_path = os.path.join(output_dir, 'pateIsoTree4V4DailySumProcessedData.csv')
        df_output.to_csv(processed_data_path, index=False)
        print(f"Processed data saved to {processed_data_path}")

if __name__ == "__main__":
    # Load data from CSV
    csv_file_path = "./SRC/Pate/HackCode/ServerInterfaceProto/[serviceName]/Data.csv"
    df = pd.read_csv(csv_file_path)
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

    # Initialize the PATE anomaly detector
    detector = PATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False, window_size=96)

    # Preprocess data to sum the values for each day
    df_resampled = detector.preprocess_data(df)

    # Add data points to the detector
    for timestamp, value in zip(df_resampled['usage_end_time'], df_resampled['cost']):
        detector.add_data(timestamp, value)

    # Detect anomalies
    score, anomalies = detector.detect_anomalies()

    if anomalies:
        print(f"Anomalies detected: {anomalies}")
    else:
        print("No anomalies detected.")

    # Save the processed data
    output_dir = os.path.dirname(csv_file_path)
    detector.save_processed_data(df_resampled, output_dir)

    # Save the attributes to a file in the same directory as the input CSV
    attributes_path = os.path.join(output_dir, 'pateIsoTree4V4DailySumAttributes.txt')
    detector.save_attributes(attributes_path)
    print(f"Attributes saved to {attributes_path}")

    # Visualize the detected anomalies
    detector.visualize_anomalies(anomalies)
    
    print("Process completed.")
