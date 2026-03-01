import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from pate.PATE_metric import PATE

class SyntheticLabelPATEAnomalyDetector:
    def __init__(self, e_buffer=100, d_buffer=100, binary_scores=False):
        self.e_buffer = e_buffer
        self.d_buffer = d_buffer
        self.binary_scores = binary_scores

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
        labels = self.generate_synthetic_labels(values)
        
        y_score = np.array(values)
        y_true = np.array(labels)

        print("Running the PATE algorithm...")
        # Apply the PATE algorithm
        result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
        print(f"PATE Score (AUC-PR): {result}")

        # Detect anomalies using an adaptive threshold based on synthetic labels
        anomalies = self._detect_anomalies(timestamps, values, y_score)
        print(f"Anomalies detected: {anomalies}")
        
        return result, anomalies

    def _detect_anomalies(self, timestamps, values, y_score):
        """
        Detects anomalies using a simple threshold.
        """
        print("Calculating threshold for anomaly detection...")
        threshold = np.mean(y_score) + 2 * np.std(y_score)  # Example threshold
        print(f"Calculated threshold: {threshold}")
        
        anomalies = [(timestamps[i], values[i]) for i in range(len(y_score)) if y_score[i] > threshold]
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

if __name__ == "__main__":
    print("Loading data from CSV...")
    
    # Load data from CSV
    df = pd.read_csv("./SRC/Data/gcp_billing_data_20240816 - gcp_billing_data_20240816.csv")
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])
    
    print("Data loaded successfully.")
    
    # Prepare data
    timestamps = df['usage_end_time'].tolist()
    values = df['cost'].tolist()

    print("Initializing the PATE anomaly detector with synthetic labels...")
    
    # Initialize the PATE anomaly detector with synthetic labels
    detector = SyntheticLabelPATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False)
    
    print("Starting the anomaly detection process...")
    
    # Detect anomalies
    score, anomalies = detector.detect_anomalies(timestamps, values)

    if anomalies:
        print(f"Anomalies detected: {anomalies}")
    else:
        print("No anomalies detected.")

    # Visualize the detected anomalies
    detector.visualize_anomalies(timestamps, values, anomalies)
    
    print("Process completed.")
