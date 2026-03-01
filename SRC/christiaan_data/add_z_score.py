import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score

# Load your data
data = pd.read_csv('original_data.csv')

# Calculate the rolling mean and standard deviation
rolling_mean = data['cost'].rolling(window=30).mean()
rolling_std = data['cost'].rolling(window=30).std()

print(rolling_mean)

# Calculate the Z-score
data['z_score'] = (data['value'] - rolling_mean) / rolling_std

# Define a threshold for anomalies
threshold = 3
data['anomaly'] = data['z_score'].apply(lambda x: 1 if np.abs(x) > threshold else 0)

data.to_csv("csvTest.csv")