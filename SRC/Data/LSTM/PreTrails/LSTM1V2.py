import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# Define the model save path
model_save_path = r".\SRC\Data\LSTM\lstm_model.h5"

print("Loading preprocessed data...")

# Load the preprocessed data
data = pd.read_csv(r".\SRC\Data\LSTM\preprocessed_data.csv")
print(f"Data loaded successfully with shape: {data.shape}")

# Step 1: Prepare the data for LSTM
# Define the sequence length
sequence_length = 10

print("Creating sequences for LSTM...")

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        if i % 100 == 0:
            print(f"Processing sequence {i}/{len(data) - seq_length}")
        x = data.iloc[i:i+seq_length].values
        y = data.iloc[i+seq_length]['usage_amount']
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

# Exclude the 'usage_end_time' column as it's not needed for LSTM
sequence_data = data.drop(columns=['usage_end_time'])

# Create sequences
X, y = create_sequences(sequence_data, sequence_length)
print(f"Sequences created. X shape: {X.shape}, y shape: {y.shape}")

# Split the data into training and test sets
print("Splitting data into training and test sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
print(f"Data split completed. Training set shape: {X_train.shape}, Test set shape: {X_test.shape}")

# Step 2: Build the LSTM Model
print("Building LSTM model...")
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(50, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(25))
model.add(Dense(1))

# Compile the model
print("Compiling the model...")
model.compile(optimizer='adam', loss='mean_squared_error')
print("Model compiled successfully.")

# Step 3: Train the LSTM Model
print("Training the LSTM model...")
history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1, verbose=2)
print("Model training completed.")

# Save the trained model to a file
print(f"Saving the model to {model_save_path}...")
model.save(model_save_path)
print("Model saved successfully.")

# Step 4: Evaluate the Model
print("Evaluating the model on training and test data...")
train_loss = model.evaluate(X_train, y_train, verbose=0)
test_loss = model.evaluate(X_test, y_test, verbose=0)
print(f"Train Loss: {train_loss}")
print(f"Test Loss: {test_loss}")

# Step 5: Make Predictions
print("Making predictions on the test set...")
y_test_pred = model.predict(X_test)
print(f"Predictions on test set completed. y_test_pred shape: {y_test_pred.shape}")

# Make predictions on the entire dataset
print("Making predictions on the entire dataset...")
y_full_pred = model.predict(X)
print(f"Predictions on entire dataset completed. y_full_pred shape: {y_full_pred.shape}")

# Optional: Inverse transform the predictions and the actual values if you scaled them
# y_test_pred = scaler.inverse_transform(y_test_pred)
# y_test = scaler.inverse_transform(y_test.reshape(-1, 1))
# y_full_pred = scaler.inverse_transform(y_full_pred)

# Step 6: Plot Results for Test Set
print("Plotting results for the test set...")
plt.figure(figsize=(12, 6))
plt.plot(y_test, color='blue', label='Actual Usage Amount (Test)')
plt.plot(y_test_pred, color='red', label='Predicted Usage Amount (Test)')
plt.title('LSTM Model - Actual vs Predicted (Test Set)')
plt.xlabel('Time Step')
plt.ylabel('Usage Amount')
plt.legend()
plt.show()
print("Test set plot displayed.")

# Step 7: Plot Results for Entire Dataset
print("Plotting results for the entire dataset...")
plt.figure(figsize=(12, 6))
plt.plot(y, color='blue', label='Actual Usage Amount (Full Dataset)')
plt.plot(y_full_pred, color='red', label='Predicted Usage Amount (Full Dataset)')
plt.title('LSTM Model - Actual vs Predicted (Entire Dataset)')
plt.xlabel('Time Step')
plt.ylabel('Usage Amount')
plt.legend()
plt.show()
print("Full dataset plot displayed.")
