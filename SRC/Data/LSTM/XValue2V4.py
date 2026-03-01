import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# Step 1: Calculate and Normalize Z-Scores
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
    
    # Initialize the MinMaxScaler and normalize z-scores
    scaler = MinMaxScaler()
    normalized_z_scores = scaler.fit_transform(np.array(fin).reshape(-1, 1))

    # Insert or update the normalized z-scores in the DataFrame
    if 'normalized_z_score' in df.columns:
        df['normalized_z_score'] = normalized_z_scores
    else:
        df.insert(4, "normalized_z_score", normalized_z_scores)

    # Save the modified DataFrame back to the CSV file
    df.to_csv(path, index=False)

# Example usage to preprocess the data and add z-scores
z_score_data_path = r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\LSTM\preprocessed_data.csv"
addZscore(z_score_data_path)

# Step 2: Load the LSTM Model and Make Predictions
# Load the saved LSTM model
model_path = r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\LSTM\1.lstm_model.h5"
model = load_model(model_path)
print("Model loaded successfully.")

# Load the preprocessed data with normalized z-scores
data = pd.read_csv(z_score_data_path)
print(f"Data loaded successfully with shape: {data.shape}")

# Prepare the data (excluding 'usage_end_time' and one additional column to match the model's expected input shape)
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

# Combine actual values, predictions, and normalized z-scores into a DataFrame
results_df = pd.DataFrame({
    'Actual_Usage_Amount': y,
    'Predicted_Usage_Amount': y_full_pred.flatten(),
    'Normalized_Predicted_Usage_Amount': y_full_pred_normalized.flatten(),
    'Normalized_Z_Score': data['normalized_z_score'][sequence_length:].values  # Aligning the z-scores with the prediction indices
})

# Step 3: Multiply the Z-Scores with the Predictions
combined_scores = results_df['Normalized_Z_Score'] * results_df['Normalized_Predicted_Usage_Amount']

# Add the combined scores to the DataFrame without normalizing this time
results_df['Combined_Score'] = combined_scores

# Step 4: Detect anomalies based on the combined score threshold
anomaly_threshold = 0.3
results_df['Anomaly'] = results_df['Combined_Score'] > anomaly_threshold

# Save the results to a new CSV file
output_path = r"C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\LSTM\original_and_combined_scores_with_anomalies.csv"
results_df.to_csv(output_path, index=False)
print(f"Original values, Combined Scores, and Anomalies saved to {output_path}")

# Optional: plot the actual vs predicted values and highlight anomalies
plt.figure(figsize=(12, 6))
plt.plot(results_df['Actual_Usage_Amount'], color='blue', label='Actual Usage Amount')
plt.plot(results_df['Combined_Score'], color='purple', label='Combined Score')
plt.scatter(results_df.index[results_df['Anomaly']], results_df['Combined_Score'][results_df['Anomaly']], 
            color='red', label='Anomaly', marker='x')
plt.title('LSTM Model - Actual vs Predicted with Z-Scores and Combined Scores')
plt.xlabel('Time Step')
plt.ylabel('Value')
plt.legend()
plt.show()
