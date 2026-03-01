import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

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

# Step 5: Initialize the Prophet model
model = Prophet()

# Step 6: Fit the model on the preprocessed data
model.fit(df_aggregated)

# Step 7: Make a future DataFrame for predictions (e.g., next 30 days)
# Here 'H' is used for hourly data, and we predict for the next 30 days
future = model.make_future_dataframe(periods=30*24, freq='H')

# Step 8: Forecast future values
forecast = model.predict(future)

# Step 9: Display the forecasted values
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])

# Step 10: Visualize the forecast
model.plot(forecast)
plt.title("Usage Amount Forecast")
plt.xlabel("Date")
plt.ylabel("Usage Amount")
plt.show()

# Step 11: Plot the components (trend, weekly, yearly seasonality)
model.plot_components(forecast)
plt.show()
