import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from pate.PATE_metric import PATE
import os

class SyntheticLabelPATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores
        self.threshold = None  # To store the calculated threshold
        self.result = None  # To store the PATE score
        self.labels = None  # To store the anomaly labels

    def preprocess_data(self, df):
        print("Starting preprocessing of data to calculate hourly sums...")

        # Ensure 'usage_end_time' is the index
        df.set_index('usage_end_time', inplace=True)

        # Select numeric columns for resampling
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df_resampled = df[numeric_columns].resample('H').sum()

        # Re-attach non-numeric columns (like usage_unit and service_type)
        df_non_numeric = df[['usage_unit', 'service_type']].resample('H').first()

        # Combine numeric and non-numeric resampled data
        df_resampled = df_resampled.join(df_non_numeric).reset_index()

        print(f"Hourly sums calculated:\n{df_resampled.head()}")
        return df_resampled

    def generate_synthetic_labels(self, values):
        print("Starting synthetic label generation using Isolation Forest...")
        
        # Use IsolationForest to generate synthetic labels
        model = IsolationForest(contamination=0.01, random_state=42)
        model.fit(np.array(values).reshape(-1, 1))
        labels = model.predict(np.array(values).reshape(-1, 1))
        
        # Convert the labels (-1 for anomaly, 1 for normal) to binary labels (1 for anomaly, 0 for normal)
        labels = np.where(labels == -1, 1, 0)
        
        print(f"Synthetic labels generated: {labels}")
        print("Synthetic label generation complete.")
        return labels

    def detect_anomalies(self, timestamps, values):
        print("Starting anomaly detection process...")
        
        # Generate synthetic labels
        self.labels = self.generate_synthetic_labels(values)
        
        y_score = np.array(values)
        y_true = np.array(self.labels)

        print("Running the PATE algorithm...")
        # Apply the PATE algorithm
        self.result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
        print(f"PATE Score (AUC-PR): {self.result}")

        # Detect anomalies using an adaptive threshold based on synthetic labels
        anomalies = self._detect_anomalies(timestamps, values, y_score)
        print(f"Anomalies detected: {anomalies}")
        
        return self.result, anomalies, self.labels

    def _detect_anomalies(self, timestamps, values, y_score):
        """
        Detects anomalies using a simple threshold.
        """
        print("Calculating threshold for anomaly detection...")
        self.threshold = np.mean(y_score) + 2 * np.std(y_score)  # Example threshold
        print(f"Calculated threshold: {self.threshold}")
        
        anomalies = [(timestamps[i], values[i]) for i in range(len(y_score)) if y_score[i] > self.threshold]
        print(f"Anomalies based on threshold: {anomalies}")
        
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
        """
        Save the attributes of the last run to a file, including anomaly labels.
        """
        with open(filepath, 'w') as f:
            f.write(f"e_buffer={self.e_buffer}\n")
            f.write(f"d_buffer={self.d_buffer}\n")
            f.write(f"binary_scores={self.binary_scores}\n")
            f.write(f"threshold={self.threshold}\n")
            f.write(f"PATE Score (AUC-PR)={self.result}\n")
            f.write(f"Anomaly Labels={self.labels.tolist()}\n")

if __name__ == "__main__":
    # Load data from CSV
    csv_file_path = "./SRC/Pate/HackCode/ServerInterfaceProto/[serviceName]/Data.csv"
    df = pd.read_csv(csv_file_path)
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])
    
    print("Data loaded successfully.")
    
    # Initialize the PATE anomaly detector with synthetic labels
    detector = SyntheticLabelPATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False)
    
    print("Preprocessing data to calculate hourly sums...")
    
    # Preprocess data to calculate hourly sums
    df_resampled = detector.preprocess_data(df)
    
    print("Starting the anomaly detection process...")
    
    # Detect anomalies
    timestamps = df_resampled['usage_end_time'].tolist()
    values = df_resampled['cost'].tolist()
    score, anomalies, labels = detector.detect_anomalies(timestamps, values)

    if anomalies:
        print(f"Anomalies detected: {anomalies}")
    else:
        print("No anomalies detected.")

    # Prepare data for output
    df_resampled['is_anomaly'] = labels
    df_resampled['reference_time'] = (df_resampled['usage_end_time'] - df_resampled['usage_end_time'].min()).dt.total_seconds() / 3600  # Reference time in hours
    
    # Select relevant columns and save to processedData.csv
    df_output = df_resampled[['reference_time', 'is_anomaly', 'usage_end_time', 'cost', 'usage_amount', 'usage_unit', 'service_type']]
    
    # Save processedData.csv in the same directory as the input CSV
    output_dir = os.path.dirname(csv_file_path)
    processed_data_path = os.path.join(output_dir, 'pateStandardDef4V4HourlySumProcessedData.csv')
    df_output.to_csv(processed_data_path, index=False)
    print(f"Processed data saved to {processed_data_path}")

    # Save the attributes to a file in the same directory as the input CSV
    attributes_path = os.path.join(output_dir, 'pateStandardDef4V4HourlyAttributes.txt')
    detector.save_attributes(attributes_path)
    print(f"Attributes saved to {attributes_path}")

    # Visualize the detected anomalies
    detector.visualize_anomalies(timestamps, values, anomalies)
    
    print("Process completed.")
