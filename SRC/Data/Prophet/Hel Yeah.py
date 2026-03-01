import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

# Function to simulate new data point based on historical data
def simulate_new_data_point(mean, std_dev, anomaly_chance=0.05):
    """
    Simulate a new data point with a certain chance of being an anomaly.
    :param mean: The mean of the historical data
    :param std_dev: The standard deviation of the historical data
    :param anomaly_chance: The probability of generating an anomaly (default is 5%)
    :return: A simulated usage amount value
    """
    if np.random.rand() < anomaly_chance:
        return np.random.normal(mean + 3 * std_dev, std_dev)  # Simulate an anomaly
    else:
        return np.random.normal(mean, std_dev)  # Simulate a normal point

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

# Step 5: Generate random data points
mean_usage = df_aggregated['y'].mean()
std_dev_usage = df_aggregated['y'].std()

# Simulate 100 new hourly data points
new_data_points = pd.DataFrame({
    'ds': pd.date_range(start=df_aggregated['ds'].max(), periods=100, freq='H'),
    'y': [simulate_new_data_point(mean_usage, std_dev_usage) for _ in range(100)]
})

# Combine the original data with the new simulated data
df_combined = pd.concat([df_aggregated, new_data_points], ignore_index=True)

# Step 6: Initialize the Prophet model
model = Prophet()

# Step 7: Fit the model on the combined data
model.fit(df_combined)

# Step 8: Make a future DataFrame for predictions (e.g., next 30 days)
# Here 'H' is used for hourly data, and we predict for the next 30 days
future = model.make_future_dataframe(periods=30*24, freq='H')

# Step 9: Forecast future values
forecast = model.predict(future)

# Step 10: Identify anomalies
df_merged = pd.merge(df_combined, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds', how='left')
df_merged['anomaly'] = df_merged.apply(lambda x: x['y'] < x['yhat_lower'] or x['y'] > x['yhat_upper'], axis=1)

# GUI Setup
root = tk.Tk()
root.title("Usage Amount Forecast with Anomalies")

# Create a figure and axis for the plot
fig, ax = plt.subplots(figsize=(10, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Step 11: Visualize the forecast with anomalies on the canvas
def plot_forecast():
    ax.clear()
    ax.plot(df_merged['ds'], df_merged['y'], label='Actual Usage Amount')
    ax.plot(forecast['ds'], forecast['yhat'], label='Forecasted Usage Amount', linestyle='--')
    ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.2, label='Forecast Range')

    # Highlight anomalies
    anomalies = df_merged[df_merged['anomaly'] == True]
    ax.scatter(anomalies['ds'], anomalies['y'], color='red', s=100, label='Anomalies')

    ax.set_title("Usage Amount Forecast with Anomalies")
    ax.set_xlabel("Date")
    ax.set_ylabel("Usage Amount")
    ax.legend()
    canvas.draw()

# Plot the forecast with anomalies when the GUI loads
plot_forecast()

# Start the Tkinter event loop
root.mainloop()
