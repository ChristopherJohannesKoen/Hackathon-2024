import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# Assume that the previous code for loading data, creating sequences, and training the model is present

# Define a threshold for detecting spikes (e.g., 2 standard deviations from the mean)
threshold = 2 * np.std(y_full_pred)

# Function to detect spikes in predictions
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
