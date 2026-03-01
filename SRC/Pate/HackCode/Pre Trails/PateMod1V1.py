import pandas as pd
from pate.PATE_metric import PATE



# Load your data into a pandas DataFrame using an absolute path
data = pd.read_csv("C:/Users/<redacted-user>/Documents/Hackathon 2024/Hackathon2024/SRC/Data/gcp_billing_data_20240816 - gcp_billing_data_20240816.csv")

# Convert the 'usage_end_time' column to datetime
data['usage_end_time'] = pd.to_datetime(data['usage_end_time'])

# Sort the data by 'usage_end_time'
data.sort_values(by='usage_end_time', inplace=True)

# Set the 'usage_end_time' as the index
data.set_index('usage_end_time', inplace=True)

# Assume your anomaly detection model outputs a score for each timestamp
y_score = data['cost'].values

# If you have ground truth labels for anomalies, load them as well
y_true = data['anomaly_label'].values if 'anomaly_label' in data.columns else None

from pate import PATE  # Ensure you import the PATE function from your installed package

# Define buffer sizes for early and delayed detection (these can be adjusted)
e_buffer = 100  # Adjust as needed
d_buffer = 100  # Adjust as needed

# If you have ground truth labels (y_true), use them; otherwise, focus on y_score
if y_true is not None:
    result = PATE(y_true, y_score, e_buffer=e_buffer, d_buffer=d_buffer, binary_scores=False)
    print("PATE Score (AUC-PR):", result)
else:
    print("Ground truth labels (y_true) not provided. Consider applying an anomaly detection model to generate y_true labels.")
