import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from pathlib import Path

# Step 1: Calculate Z-Scores and Normalize Them
def calculate_z_scores(usage_amount):
    print("Calculating z-scores for 'usage_amount' column...")
    z_scores = stats.zscore(np.log1p(usage_amount))  # Apply log1p transformation to reduce large value effect
    print(f"Z-scores calculated: mean={np.mean(z_scores):.4f}, std={np.std(z_scores):.4f}")
    
    scaler = MinMaxScaler()
    normalized_z_scores = scaler.fit_transform(z_scores.reshape(-1, 1))
    print("Z-scores normalized.")
    
    return normalized_z_scores.flatten()

# Resolve paths relative to the repository root for portability.
repo_root = Path(__file__).resolve().parents[3]
model_path = repo_root / "SRC" / "Data" / "LSTM" / "1.lstm_model.h5"
data_path = repo_root / "SRC" / "Data" / "split_data" / "Cloud Storage TEST DO NOT USE.csv"

if not model_path.exists():
    raise FileNotFoundError(f"LSTM model not found: {model_path}")

if not data_path.exists():
    raise FileNotFoundError(f"Input data file not found: {data_path}")

# Load the LSTM model
print(f"Loading LSTM model from {model_path}...")
model = load_model(str(model_path))
print("Model loaded successfully.")

# Load the specific dataset
print(f"Loading data from {data_path}...")
data = pd.read_csv(data_path)
print(f"Data loaded successfully with shape: {data.shape}")

# Convert 'usage_end_time' to datetime
print("Converting 'usage_end_time' to datetime...")
data['usage_end_time'] = pd.to_datetime(data['usage_end_time'])

# Check for and handle duplicates
print("Checking for duplicates in 'usage_end_time'...")
if data.duplicated(subset='usage_end_time').any():
    print("Duplicates found. Aggregating duplicate entries...")
    data = data.groupby('usage_end_time').agg({
        'usage_amount': 'sum',
        'cost': 'sum',
        'service_type': lambda x: x.mode()[0] if not x.mode().empty else 'Unknown'
    }).reset_index()

# Reindex to ensure all timestamps are present
print("Reindexing data to ensure all hourly timestamps are present...")
data = data.set_index('usage_end_time')
all_hours = pd.date_range(start=data.index.min(), end=data.index.max(), freq='H')
data = data.reindex(all_hours, fill_value=0).reset_index().rename(columns={'index': 'usage_end_time'})

# Aggregate data by hourly usage (This step may be redundant depending on previous aggregation)
print("Aggregating data by hourly intervals...")
hourly_data = data.resample('H', on='usage_end_time').agg({
    'usage_amount': 'sum',
    'cost': 'sum',
    'service_type': lambda x: x.mode()[0] if not x.mode().empty else 'Unknown'
}).reset_index()

print(f"Hourly aggregated data shape: {hourly_data.shape}")

# Convert 'service_type' to a string to ensure uniform data type
hourly_data['service_type'] = hourly_data['service_type'].astype(str)

# Preserve 'usage_amount' for later use
usage_amount = hourly_data['usage_amount'].values
print(f"Preserved 'usage_amount' with {len(usage_amount)} entries.")

# One-Hot Encode categorical variables
print("One-Hot Encoding 'service_type' column...")
encoder = OneHotEncoder(sparse_output=False)
encoded_features = encoder.fit_transform(hourly_data[['service_type']])
print(f"One-Hot Encoding completed. Encoded features shape: {encoded_features.shape}")

# Create a DataFrame with the encoded features
encoded_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(['service_type']))

# Concatenate the encoded features with the original DataFrame
print("Concatenating encoded features with original data...")
hourly_data = pd.concat([hourly_data.drop(columns=['service_type', 'usage_end_time']), encoded_df], axis=1)
print(f"Data shape after concatenation: {hourly_data.shape}")

# Ensure the number of features matches the model's input
expected_features = model.input_shape[-1]
current_features = hourly_data.shape[1]
print(f"Expected features: {expected_features}, Current features: {current_features}")

if current_features != expected_features:
    if current_features > expected_features:
        print(f"Warning: Model expects {expected_features} features, but the data has {current_features}. Truncating to match the expected number of features.")
        hourly_data = hourly_data.iloc[:, :expected_features]
    else:
        print(f"Padding data with {expected_features - current_features} zeros to match the expected features.")
        padding = np.zeros((hourly_data.shape[0], expected_features - current_features))
        hourly_data = np.hstack((hourly_data.values, padding))
        hourly_data = pd.DataFrame(hourly_data)
        print(f"Data shape after padding: {hourly_data.shape}")

# Calculate z-scores and normalize them
normalized_z_scores = calculate_z_scores(usage_amount)

# Moving window parameters
window_size = 50
step_size = 1

print(f"Starting sliding window predictions with window size: {window_size} and step size: {step_size}...")

# Initialize lists to store results
y_full_pred = []
y_actual = []

# Sliding window over the data
for i in range(0, len(hourly_data) - window_size, step_size):
    if i % 10 == 0:
        print(f"Processing window {i} of {len(hourly_data) - window_size}...")
    
    window_data = hourly_data.iloc[i:i+window_size].values.astype(np.float32)
    y_actual.append(usage_amount[i + window_size])
    
    window_data = window_data.reshape(1, window_size, -1)
    pred = model.predict(window_data)
    y_full_pred.append(pred[0, 0])

# Normalize the predictions
print("Normalizing predictions...")
scaler = MinMaxScaler()
y_full_pred_normalized = scaler.fit_transform(np.array(y_full_pred).reshape(-1, 1)).flatten()

# Calculate the combined score
print("Calculating combined scores...")
combined_scores = normalized_z_scores[window_size:] * y_full_pred_normalized

# Plot the actual vs combined scores
print("Plotting the results...")
plt.figure(figsize=(12, 6))
plt.plot(y_actual, color='blue', label='Actual Usage Amount')
plt.plot(combined_scores, color='purple', label='Combined Score')
plt.title('Actual Usage Amount vs Combined Score with Moving Time Frame')
plt.xlabel('Time Step')
plt.ylabel('Value')
plt.legend()
plt.show()
