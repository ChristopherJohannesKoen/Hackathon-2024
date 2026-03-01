import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

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

# Step 4: Evaluate the Model
print("Evaluating the model on training and test data...")
train_loss = model.evaluate(X_train, y_train, verbose=0)
test_loss = model.evaluate(X_test, y_test, verbose=0)
print(f"Train Loss: {train_loss}")
print(f"Test Loss: {test_loss}")

# Step 5: Make Predictions
print("Making predictions on the test set...")
y_pred = model.predict(X_test)
print(f"Predictions completed. y_pred shape: {y_pred.shape}")

# Optional: Inverse transform the predictions and the actual values if you scaled them
# y_pred = scaler.inverse_transform(y_pred)
# y_test = scaler.inverse_transform(y_test.reshape(-1, 1))

# Step 6: Plot Results
print("Plotting results...")
plt.figure(figsize=(12, 6))
plt.plot(y_test, color='blue', label='Actual Usage Amount')
plt.plot(y_pred, color='red', label='Predicted Usage Amount')
plt.title('LSTM Model - Actual vs Predicted')
plt.xlabel('Time Step')
plt.ylabel('Usage Amount')
plt.legend()
plt.show()
print("Plot displayed.")
