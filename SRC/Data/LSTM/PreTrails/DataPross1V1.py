import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

# Load the data into a DataFrame
data = pd.read_csv("./SRC/Data/gcp_billing_data_20240816 - gcp_billing_data_20240816.csv")

# Step 1: Handle Missing Values
# Fill missing values in usage_amount with 0 or use forward-fill/backward-fill based on the scenario
data['usage_amount'].fillna(0, inplace=True)

# Step 2: Feature Engineering
# Convert usage_end_time to datetime format
data['usage_end_time'] = pd.to_datetime(data['usage_end_time'])

# Extract time-based features
data['hour'] = data['usage_end_time'].dt.hour
data['day_of_week'] = data['usage_end_time'].dt.dayofweek
data['day_of_month'] = data['usage_end_time'].dt.day
data['month'] = data['usage_end_time'].dt.month

# Step 3: Handle Unknown Variables
# Encoding categorical variables (service_type, region) - handle unknowns with 'ignore' strategy
data['service_type'] = data['service_type'].astype('category')
data['region'] = data['region'].astype('category')

# For any unseen categories during encoding, we'll use a placeholder value or drop those rows
data['service_type'] = data['service_type'].cat.add_categories(['unknown']).fillna('unknown')
data['region'] = data['region'].cat.add_categories(['unknown']).fillna('unknown')

# Convert categorical variables to numeric codes
data['service_type'] = data['service_type'].cat.codes
data['region'] = data['region'].cat.codes

# Step 4: Data Normalization
# Use MinMaxScaler to normalize the usage_amount column
scaler = MinMaxScaler(feature_range=(0, 1))
data['usage_amount'] = scaler.fit_transform(data['usage_amount'].values.reshape(-1, 1))

# Normalize the additional features if needed
data[['hour', 'day_of_week', 'day_of_month', 'month']] = scaler.fit_transform(
    data[['hour', 'day_of_week', 'day_of_month', 'month']]
)

# Step 5: Sequence Generation
# Define the sequence length
sequence_length = 10

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data.iloc[i:i+seq_length].values
        y = data.iloc[i+seq_length]['usage_amount']
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

# We include all features in the sequence generation
sequence_data = data[['usage_amount', 'service_type', 'region', 'hour', 'day_of_week', 'day_of_month', 'month']]
X, y = create_sequences(sequence_data, sequence_length)

# Step 6: Reshape Data for LSTM
# Reshape the input data to the 3D format (samples, time steps, features)
X = X.reshape((X.shape[0], X.shape[1], X.shape[2]))

# Output shapes
print(f'Shape of X: {X.shape}')
print(f'Shape of y: {y.shape}')

# X is now ready to be fed into the LSTM model
