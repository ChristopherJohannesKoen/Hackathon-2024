import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# Step 1: Calculate Z-Scores and Normalize Them
def calculate_z_scores(data):
    c = 10
    n = len(data) / c
    fin = []
    
    for i in range(1, c + 1):
        pre = int(n * (i - 1))
        post = int(n * i)
        temp = data.iloc[pre:post]
        z = np.array(temp["usage_amount"])
        zstat = list(stats.zscore(z))
        fin.extend(zstat)
    
    # Normalize the z-scores
    scaler = MinMaxScaler()
    normalized_z_scores = scaler.fit_transform(np.array(fin).reshape(-1, 1))
    
    return normalized_z_scores.flatten()

# Load the LSTM model
model_path = r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\LSTM\1.lstm_model.h5"
model = load_model(model_path)
print("Model loaded successfully.")

# Load the specific dataset
data_path = r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\gcp_billing_data_20240816 - gcp_billing_data_20240816.csv"
data = pd.read_csv(data_path)
print(f"Data loaded successfully with shape: {data.shape}")

# Drop non-numeric columns that are not useful for the model
data = data.drop(columns=['usage_end_time', 'usage_unit'])

# One-Hot Encode categorical variables
encoder = OneHotEncoder(sparse=False)
encoded_features = encoder.fit_transform(data[['service_type', 'region']])

# Create a DataFrame with the encoded features
encoded_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(['service_type', 'region']))

# Concatenate the encoded features with the original DataFrame
data = pd.concat([data.drop(columns=['service_type', 'region']), encoded_df], axis=1)

# Calculate z-scores and normalize them
normalized_z_scores = calculate_z_scores(data)

# Ensure the number of features matches the model's input
expected_features = model.input_shape[-1]  # Number of features the model expects
current_features = data.shape[1]

if current_features > expected_features:
    drop_columns = data.columns[expected_features:]  # Columns to drop
    data = data.drop(columns=drop_columns)
elif current_features < expected_features:
    raise ValueError(f"Model expects {expected_features} features, but the data has {current_features} features.")

# Moving window parameters
window_size = 50000
step_size = 25000

# Initialize lists to store results
y_full_pred = []
y_actual = []

# Sliding window over the data
for i in range(0, len(data) - window_size, step_size):
    window_data = data.iloc[i:i+window_size].values.astype(np.float32)  # Ensure the data is in float32
    y_actual.append(data.iloc[i + window_size]['usage_amount'])
    
    # Reshape the window data for prediction
    window_data = window_data.reshape(1, window_size, -1)
    
    # Predict the next value
    pred = model.predict(window_data)
    y_full_pred.append(pred[0, 0])

# Normalize the predictions
scaler = MinMaxScaler()
y_full_pred_normalized = scaler.fit_transform(np.array(y_full_pred).reshape(-1, 1)).flatten()

# Calculate the combined score
combined_scores = normalized_z_scores[window_size:] * y_full_pred_normalized

# Plot the actual vs combined scores
plt.figure(figsize=(12, 6))
plt.plot(y_actual, color='blue', label='Actual Usage Amount')
plt.plot(combined_scores, color='purple', label='Combined Score')
plt.title('Actual Usage Amount vs Combined Score with Moving Time Frame')
plt.xlabel('Time Step')
plt.ylabel('Value')
plt.legend()
plt.show()
