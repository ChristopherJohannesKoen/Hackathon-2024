import pandas as pd

# Step 5: You can now proceed to fit the Prophet model
from prophet import Prophet

# Step 1: Load the CSV file
file_path = r'C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\gcp_billing_data_20240816 - gcp_billing_data_20240816.csv'
df = pd.read_csv(file_path)

# Step 2: Convert 'usage_end_time' to datetime
df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

# Step 3: Aggregate or filter (if needed)
# For example, summing 'usage_amount' by 'usage_end_time'
df_aggregated = df.groupby('usage_end_time')['usage_amount'].sum().reset_index()

# Step 4: Rename columns for Prophet
df_aggregated.rename(columns={'usage_end_time': 'ds', 'usage_amount': 'y'}, inplace=True)

# Now, the data is ready to be used with Prophet

# Initialize the Prophet model
model = Prophet()

# Fit the model on the preprocessed data
model.fit(df_aggregated)

# Make a future DataFrame for predictions (e.g., next 30 days)
future = model.make_future_dataframe(periods=30, freq='H')  # 'H' for hourly data

# Forecast future values
forecast = model.predict(future)

# Display the forecasted values
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])
