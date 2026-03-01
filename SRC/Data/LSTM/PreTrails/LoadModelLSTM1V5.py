import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

# Load the saved LSTM model
model_path = r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\LSTM\1.lstm_model.h5"
model = load_model(model_path)
print("Model loaded successfully.")

# Load the preprocessed data
data = pd.read_csv(r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\LSTM\preprocessed_data.csv")
print(f"Data loaded successfully with shape: {data.shape}")

# Prepare the data (excluding 'usage_end_time' and one additional column to match the model's expected input shape)
# Assume we need to drop the 'normalized_z_score' column to match the model's expected input shape
sequence_data = data.drop(columns=['usage_end_time', 'normalized_z_score'])  # Drop 'normalized_z_score'

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data.iloc[i:i+seq_length].values
        y = data.iloc[i+seq_length]['usage_amount']
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

sequence_length = 10
X, y = create_sequences(sequence_data, sequence_length)
print(f"Sequences created. X shape: {X.shape}, y shape: {y.shape}")

# Make predictions on the entire dataset
y_full_pred = model.predict(X)
print(f"Predictions on entire dataset completed. y_full_pred shape: {y_full_pred.shape}")

# Normalize the predictions
scaler = MinMaxScaler()
y_full_pred_normalized = scaler.fit_transform(y_full_pred)

# Combine actual values and predictions into a DataFrame
results_df = pd.DataFrame({
    'Actual_Usage_Amount': y,
    'Predicted_Usage_Amount': y_full_pred.flatten(),
    'Normalized_Predicted_Usage_Amount': y_full_pred_normalized.flatten()
})

# Save the results to a CSV file
output_path = r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\LSTM\predictions.csv"
results_df.to_csv(output_path, index=False)
print(f"Predictions saved to {output_path}")

# Optional: plot the actual vs predicted values
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(y, color='blue', label='Actual Usage Amount')
plt.plot(y_full_pred, color='red', label='Predicted Usage Amount')
plt.plot(y_full_pred_normalized, color='orange', label='Normalized Predicted Usage Amount')
plt.title('LSTM Model - Actual vs Predicted (Full Dataset)')
plt.xlabel('Time Step')
plt.ylabel('Usage Amount')
plt.legend()
plt.show()
