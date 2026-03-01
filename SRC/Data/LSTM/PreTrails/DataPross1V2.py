import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

# Load the data into a DataFrame
data = pd.read_csv("./SRC/Data/gcp_billing_data_20240816 - gcp_billing_data_20240816.csv")

# Step 1: Handle Missing Values
data['usage_amount'].fillna(0, inplace=True)

# Step 2: Feature Engineering
data['usage_end_time'] = pd.to_datetime(data['usage_end_time'])

# Extract time-based features
data['hour'] = data['usage_end_time'].dt.hour
data['day_of_week'] = data['usage_end_time'].dt.dayofweek
data['day_of_month'] = data['usage_end_time'].dt.day
data['month'] = data['usage_end_time'].dt.month

# Step 3: Handle Unknown Variables
data['service_type'] = data['service_type'].astype('category')
data['region'] = data['region'].astype('category')

data['service_type'] = data['service_type'].cat.add_categories(['unknown']).fillna('unknown')
data['region'] = data['region'].cat.add_categories(['unknown']).fillna('unknown')

# Convert categorical variables to numeric codes
data['service_type'] = data['service_type'].cat.codes
data['region'] = data['region'].cat.codes

# Step 4: Data Normalization
scaler = MinMaxScaler(feature_range=(0, 1))
data['usage_amount'] = scaler.fit_transform(data['usage_amount'].values.reshape(-1, 1))

data[['hour', 'day_of_week', 'day_of_month', 'month']] = scaler.fit_transform(
    data[['hour', 'day_of_week', 'day_of_month', 'month']]
)

# Step 5: Save Preprocessed Data to CSV
# Define the file path
file_path = "./SRC/Data/LSTM/preprocessed_data.csv"

# Select the relevant columns to save in the new CSV file
columns_to_save = ['usage_end_time', 'usage_amount', 'service_type', 'region', 'hour', 'day_of_week', 'day_of_month', 'month']
preprocessed_data = data[columns_to_save]

# Save the preprocessed data to the specified path
preprocessed_data.to_csv(file_path, index=False)

print(f"Preprocessed data saved to '{file_path}'")
