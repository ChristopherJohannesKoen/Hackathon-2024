import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# Function to add z-score and normalize it
def addZscore(path):
    df = pd.read_csv(path)
    c = 10
    n = len(df) / c
    fin = []
    
    for i in range(1, c + 1):
        pre = int(n * (i - 1))
        post = int(n * i)
        temp = df.iloc[pre:post]
        z = np.array(temp["usage_amount"])
        zstat = list(stats.zscore(z))
        fin.extend(zstat)
    
    # Normalize the z-scores
    scaler = MinMaxScaler()
    normalized_z_scores = scaler.fit_transform(np.array(fin).reshape(-1, 1))

    # Insert normalized z-scores into the DataFrame
    df['normalized_z_score'] = normalized_z_scores

    # Save the modified DataFrame back to the CSV file
    df.to_csv(path, index=False)

# Example usage to preprocess the data and add z-scores
z_score_data_path = r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\LSTM\preprocessed_data.csv"
addZscore(z_score_data_path)

# Load the saved LSTM model
model_path = r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\LSTM\1.lstm_model.h5"
model = load_model(model_path)
print("Model loaded successfully.")

# Load the preprocessed data with normalized z-scores
data = pd.read_csv(z_score_data_path)
print(f"Data loaded successfully with shape: {data.shape}")

# Prepare the data (excluding 'usage_end_time' and 'normalized_z_score' to match model input)
sequence_length = 10
sequence_data = data.drop(columns=['usage_end_time', 'normalized_z_score'])  # Drop the normalized_z_score column

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data.iloc[i:i+seq_length].values
        y = data.iloc[i+seq_length]['usage_amount']
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

# Create sequences
X, y = create_sequences(sequence_data, sequence_length)
print(f"Sequences created. X shape: {X.shape}, y shape: {y.shape}")

# Make predictions on the entire dataset
y_full_pred = model.predict(X)
print(f"Predictions on entire dataset completed. y_full_pred shape: {y_full_pred.shape}")

# Define a threshold for detecting spikes (e.g., 2 standard deviations from the mean of predictions)
threshold = 2 * np.std(y_full_pred)

def detect_spikes(predictions, threshold):
    spikes = []
    for i in range(len(predictions)):
        if predictions[i] > threshold:
            spikes.append(i)
    return spikes

# Detect spikes in the full dataset predictions
spike_indices = detect_spikes(y_full_pred, threshold)
print(f"Spikes detected at indices: {spike_indices}")

# Plot the results with spikes highlighted
plt.figure(figsize=(12, 6))
plt.plot(y, color='blue', label='Actual Usage Amount (Full Dataset)')
plt.plot(y_full_pred, color='red', label='Predicted Usage Amount (Full Dataset)')
plt.scatter(spike_indices, y_full_pred[spike_indices], color='green', marker='x', label='Detected Spikes')
plt.title('LSTM Model - Actual vs Predicted (Entire Dataset) with Spike Detection')
plt.xlabel('Time Step')
plt.ylabel('Usage Amount')
plt.legend()
plt.show()

if spike_indices:
    print(f"Warning: {len(spike_indices)} usage spikes detected!")
    # You could add more sophisticated alert mechanisms here, like sending an email or logging the event.
else:
    print("No usage spikes detected.")
