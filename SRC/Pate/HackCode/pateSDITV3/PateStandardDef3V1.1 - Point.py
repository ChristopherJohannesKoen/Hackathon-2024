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

    def generate_synthetic_labels(self, values):
        print("Starting synthetic label generation using Isolation Forest...")
        
        # Remove NaN values from the values array before fitting the model
        non_nan_values = np.array(values).reshape(-1, 1)
        non_nan_values = non_nan_values[~np.isnan(non_nan_values)]
        non_nan_values = non_nan_values.reshape(-1, 1)

        # Use IsolationForest to generate synthetic labels
        model = IsolationForest(contamination=0.01, random_state=42)
        model.fit(non_nan_values)
        labels = model.predict(non_nan_values)
        
        # Convert the labels (-1 for anomaly, 1 for normal) to binary labels (1 for anomaly, 0 for normal)
        labels = np.where(labels == -1, 1, 0)
        
        print(f"Synthetic labels generated: {labels}")
        print("Synthetic label generation complete.")
        return labels

    def detect_anomalies(self, timestamps, values):
        print("Starting anomaly detection process...")
        
        # Filter out NaN values from both timestamps and values
        non_nan_mask = ~np.isnan(values)
        filtered_timestamps = [timestamps[i] for i in range(len(timestamps)) if non_nan_mask[i]]
        filtered_values = [values[i] for i in range(len(values)) if non_nan_mask[i]]

        # Generate synthetic labels
        labels = self.generate_synthetic_labels(filtered_values)
        self.labels = labels  # Store labels
        
        y_score = np.array(filtered_values)
        y_true = np.array(labels)

        print("Running the PATE algorithm...")
        # Apply the PATE algorithm
        self.result = PATE(y_true, y_score, e_buffer=self.e_buffer, d_buffer=self.d_buffer, binary_scores=self.binary_scores)
        print(f"PATE Score (AUC-PR): {self.result}")

        # Detect anomalies using an adaptive threshold based on synthetic labels
        anomalies = self._detect_anomalies(filtered_timestamps, filtered_values, y_score)
        print(f"Anomalies detected: {anomalies}")
        
        return self.result, anomalies, labels

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
        
        # Filter out NaT values from timestamps and corresponding values
        valid_mask = pd.notna(timestamps)
        valid_timestamps = [timestamps[i] for i in range(len(timestamps)) if valid_mask[i]]
        valid_values = [values[i] for i in range(len(values)) if valid_mask[i]]

        plt.figure(figsize=(14, 7))
        plt.plot(valid_timestamps, valid_values, label='Time Series Data')
        
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
        Save the attributes of the last run to a file.
        """
        with open(filepath, 'w') as f:
            f.write(f"e_buffer={self.e_buffer}\n")
            f.write(f"d_buffer={self.d_buffer}\n")
            f.write(f"binary_scores={self.binary_scores}\n")
            f.write(f"threshold={self.threshold}\n")
            f.write(f"PATE Score (AUC-PR)={self.result}\n")
            f.write(f"Anomaly Labels={self.labels.tolist()}\n")

if __name__ == "__main__":
    print("Loading data from CSV...")
    
    # Load data from CSV
    csv_file_path = "./SRC/Pate/HackCode/ServerInterfaceProto/[serviceName]/Data.csv"
    df = pd.read_csv(csv_file_path)
    df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])
    
    print("Data loaded successfully.")
    
    # Prepare data
    df['reference_time'] = (df['usage_end_time'] - df['usage_end_time'].min()).dt.total_seconds() / 3600  # Reference time in hours

    # Generate all possible hourly reference times
    min_time = df['reference_time'].min()
    max_time = df['reference_time'].max()
    all_hours = pd.DataFrame({'reference_time': np.arange(min_time, max_time + 1)})

    # Merge with original data to fill in missing hours
    df = all_hours.merge(df, on='reference_time', how='left')

    # Handle duplicates by adding a suffix
    df['suffix'] = df.groupby('reference_time').cumcount() + 1
    df['suffix'] = df['suffix'].apply(lambda x: f"{x}" if x > 1 else "")

    # Combine the reference_time and suffix
    df['reference_time'] = df['reference_time'].astype(str) + df['suffix']

    # Extract timestamps and values after filling in missing hours
    timestamps = df['usage_end_time'].tolist()
    values = df['cost'].tolist()

    print("Initializing the PATE anomaly detector with synthetic labels...")
    
    # Initialize the PATE anomaly detector with synthetic labels
    detector = SyntheticLabelPATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False)
    
    print("Starting the anomaly detection process...")
    
    # Detect anomalies
    score, anomalies, labels = detector.detect_anomalies(timestamps, values)

    if anomalies:
        print(f"Anomalies detected: {anomalies}")
    else:
        print("No anomalies detected.")

    # Prepare data for output
    df['is_anomaly'] = np.nan
    df.loc[df['cost'].notna(), 'is_anomaly'] = labels
    
    # Select relevant columns
    df_output = df[['reference_time', 'is_anomaly', 'usage_end_time', 'cost', 'usage_amount', 'usage_unit', 'service_type']]
    
    # Save processedData.csv in the same directory as the input CSV
    output_dir = os.path.dirname(csv_file_path)
    processed_data_path = os.path.join(output_dir, 'pateStandardDef3V1PointProcessedData.csv')
    df_output.to_csv(processed_data_path, index=False)
    print(f"Processed data saved to {processed_data_path}")

    # Save the attributes to a file in the same directory as the input CSV
    attributes_path = os.path.join(output_dir, 'pateStandardDef3V1PointProcessedAttributes.txt')
    detector.save_attributes(attributes_path)
    print(f"Attributes saved to {attributes_path}")

    # Visualize the detected anomalies
    detector.visualize_anomalies(timestamps, values, anomalies)
    
    print("Process completed.")
