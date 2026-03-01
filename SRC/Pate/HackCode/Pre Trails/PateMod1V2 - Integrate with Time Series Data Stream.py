import numpy as np
import pandas as pd
from pate.PATE_metric import PATE
from datetime import datetime, timedelta
from collections import deque

import numpy as np
import pandas as pd
from pate.PATE_metric import PATE
from datetime import datetime, timedelta
from collections import deque

class PATEAnomalyDetector:
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
    
    def detect_anomalies(self):
        """
        Applies the PATE algorithm to detect anomalies in the time series data.
        
        :return: The PATE score (AUC-PR) and any detected anomalies.
        """
        # Convert the deque to a numpy array for processing
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

        # Optionally return detected anomalies
        anomalies = self._detect_anomalies(y_score)
        return result, anomalies

    def _detect_anomalies(self, y_score):
        """
        Detects anomalies based on the PATE score.

        :param y_score: The predicted scores for each data point.
        :return: A list of anomalies.
        """
        threshold = np.mean(y_score) + 2 * np.std(y_score)  # Example threshold
        anomalies = [(timestamp, value) for timestamp, value in zip(self.time_series_data, y_score) if value > threshold]
        return anomalies
    
    def clear_data(self):
        """
        Clears the stored time series data and labels.
        """
        self.time_series_data.clear()
        self.labels.clear()



if __name__ == "__main__":
    # Example of how to use the PATEAnomalyDetector with a simulated data stream
    detector = PATEAnomalyDetector(e_buffer=100, d_buffer=100, binary_scores=False)
    
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
            score, anomalies = detector.detect_anomalies()
            if anomalies:
                print(f"Anomalies detected: {anomalies}")
            else:
                print("No anomalies detected.")

    # Clear the data after processing
    detector.clear_data()
