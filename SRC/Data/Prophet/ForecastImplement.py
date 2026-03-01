import pandas as pd
import numpy as np
from prophet import Prophet
import time
import matplotlib.pyplot as plt

# Step 1: Load your historical cloud cost data
file_path = r'./SRC/Data/Prophet/gcp_billing_data_20240816 - gcp_billing_data_20240816.csv'
df = pd.read_csv(file_path)

# Step 2: Convert 'usage_end_time' to datetime
df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

# Step 3: Filter out the last few data points to avoid the dip
# Here, we exclude the last 3 data points (adjust as necessary)
df_aggregated = df.groupby('usage_end_time')['cost'].sum().reset_index()
df_aggregated = df_aggregated.iloc[:-3]  # Exclude the last 3 data points

# Step 4: Rename columns for Prophet
df_aggregated.rename(columns={'usage_end_time': 'ds', 'cost': 'y'}, inplace=True)

# Step 5: Function to simulate new data point based on historical data
def simulate_new_data_point(mean, std_dev, anomaly_chance=0.05):
    """
    Simulate a new data point with a certain chance of being an anomaly.
    :param mean: The mean of the historical data
    :param std_dev: The standard deviation of the historical data
    :param anomaly_chance: The probability of generating an anomaly (default is 5%)
    :return: A simulated cost value
    """
    if np.random.rand() < anomaly_chance:
        return np.random.normal(mean + 3 * std_dev, std_dev)  # Simulate an anomaly
    else:
        return np.random.normal(mean, std_dev)  # Simulate a normal point

# Step 6: Set up real-time prediction and anomaly detection
def detect_anomalies(new_data, historical_data):
    model = Prophet()
    df_aggregated_new = pd.concat([historical_data, new_data], ignore_index=True)
    
    model.fit(df_aggregated_new)
    future = model.make_future_dataframe(periods=1, freq='H')
    forecast = model.predict(future)
    
    last_actual = new_data.iloc[-1]['y']
    last_forecast = forecast.iloc[-1]
    
    if last_actual < last_forecast['yhat_lower'] or last_actual > last_forecast['yhat_upper']:
        print(f"Anomaly detected at {last_forecast['ds']}: Actual={last_actual}, Forecast={last_forecast['yhat']}")
        return True, last_forecast['ds'], last_actual, last_forecast['yhat']
    else:
        print(f"No anomaly at {last_forecast['ds']}: Actual={last_actual}, Forecast={last_forecast['yhat']}")
        return False, last_forecast['ds'], last_actual, last_forecast['yhat']

# Step 7: Calculate mean and standard deviation from filtered historical data
mean_cost = df_aggregated['y'].mean()
std_dev_cost = df_aggregated['y'].std()

# Example real-time loop with simulated data points
while True:
    new_data_point = pd.DataFrame({
        'ds': [pd.to_datetime('now')],
        'y': [simulate_new_data_point(mean_cost, std_dev_cost)]
    })
    
    anomaly_detected, ds, actual, forecasted = detect_anomalies(new_data_point, df_aggregated)
    
    if anomaly_detected:
        with open('anomaly_log.csv', 'a') as f:
            f.write(f"{ds},{actual},{forecasted}\n")
    
    plt.figure(figsize=(10, 6))
    plt.plot(df_aggregated['ds'], df_aggregated['y'], label='Historical Cost')
    plt.scatter(new_data_point['ds'], new_data_point['y'], color='red', label='New Data Point')
    plt.legend()
    plt.title("Real-Time Anomaly Detection")
    plt.show()
    
    time.sleep(1)  # Adjust the sleep time as needed
