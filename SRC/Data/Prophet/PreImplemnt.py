import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Step 1: Load your cloud cost data
file_path = r'C:\Users\<redacted-user>\Documents\Hackathon 2024\Hackathon2024\SRC\Data\gcp_billing_data_20240816 - gcp_billing_data_20240816.csv'
df = pd.read_csv(file_path)

# Step 2: Convert 'usage_end_time' to datetime
df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

# Step 3: Aggregate the cost by 'usage_end_time' (if necessary)
df_aggregated = df.groupby('usage_end_time')['cost'].sum().reset_index()

# Step 4: Rename columns for Prophet
df_aggregated.rename(columns={'usage_end_time': 'ds', 'cost': 'y'}, inplace=True)

# Step 5: Initialize the Prophet model
model = Prophet()

# Step 6: Fit the model on the preprocessed data
model.fit(df_aggregated)

# Step 7: Make a future DataFrame for predictions
# Forecasting the next 24 hours (or adjust as needed)
future = model.make_future_dataframe(periods=24, freq='H')

# Step 8: Generate forecast
forecast = model.predict(future)

# Step 9: Compare actual cost with forecast
# Merging the forecast with the actual data for comparison
df_merged = pd.merge(df_aggregated, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds', how='left')

# Step 10: Detect anomalies
df_merged['anomaly'] = df_merged.apply(lambda x: 'Yes' if x['y'] < x['yhat_lower'] or x['y'] > x['yhat_upper'] else 'No', axis=1)

# Step 11: Visualize anomalies
plt.figure(figsize=(10, 6))
plt.plot(df_merged['ds'], df_merged['y'], label='Actual Cost')
plt.plot(df_merged['ds'], df_merged['yhat'], label='Forecasted Cost')
plt.fill_between(df_merged['ds'], df_merged['yhat_lower'], df_merged['yhat_upper'], color='gray', alpha=0.3)
plt.scatter(df_merged['ds'][df_merged['anomaly'] == 'Yes'], df_merged['y'][df_merged['anomaly'] == 'Yes'], color='red', label='Anomaly')
plt.legend()
plt.title("Cloud Cost Anomaly Detection")
plt.xlabel("Date")
plt.ylabel("Cost")
plt.show()

# Step 12: Save the results (optional)
# Save the anomalies to a CSV file for further analysis or logging
df_merged.to_csv('cloud_cost_anomaly_detection_results.csv', index=False)
