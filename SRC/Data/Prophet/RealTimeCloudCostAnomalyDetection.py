import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

# Function to simulate new data point based on historical data
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

# Function to detect anomalies
def detect_anomalies(new_data, historical_data):
    # Disable trend in Prophet by setting growth='flat'
    model = Prophet(growth='flat')
    df_aggregated_new = pd.concat([historical_data, new_data], ignore_index=True)
    
    model.fit(df_aggregated_new)
    future = model.make_future_dataframe(periods=1, freq='H')
    forecast = model.predict(future)
    
    last_actual = new_data.iloc[-1]['y']
    last_forecast = forecast.iloc[-1]
    
    # Debug: Print the forecasted values for verification
    print(f"Forecasted: {last_forecast['ds']} | yhat: {last_forecast['yhat']} | yhat_lower: {last_forecast['yhat_lower']} | yhat_upper: {last_forecast['yhat_upper']}")

    if last_actual < last_forecast['yhat_lower'] or last_actual > last_forecast['yhat_upper']:
        return True, last_forecast['ds'], last_actual, last_forecast['yhat'], last_forecast['yhat_lower'], last_forecast['yhat_upper']
    else:
        return False, last_forecast['ds'], last_actual, last_forecast['yhat'], last_forecast['yhat_lower'], last_forecast['yhat_upper']

# Function to update the graph with new data points and detect anomalies
def update_graph():
    global df_aggregated, mean_cost, std_dev_cost, anomaly_log
    
    # Calculate mean and standard deviation based on the last 100,000 data points
    if len(df_aggregated) > 10000:
        recent_data = df_aggregated.tail(10000)
    else:
        recent_data = df_aggregated
    
    mean_cost = recent_data['y'].mean()
    std_dev_cost = recent_data['y'].std()
    
    new_data_point = pd.DataFrame({
        'ds': [pd.to_datetime('now')],
        'y': [simulate_new_data_point(mean_cost, std_dev_cost)]
    })
    
    anomaly_detected, ds, actual, forecasted, yhat_lower, yhat_upper = detect_anomalies(new_data_point, df_aggregated)
    
    # Append new data point to the historical data
    df_aggregated = pd.concat([df_aggregated, new_data_point], ignore_index=True)
    
    # Update the plot
    ax.clear()
    ax.plot(df_aggregated['ds'], df_aggregated['y'], label='Historical Cost')
    ax.fill_between(df_aggregated['ds'], yhat_lower, yhat_upper, color='gray', alpha=0.2, label='Forecasted Range')
    ax.scatter(new_data_point['ds'], new_data_point['y'], color='red', s=100, label='New Data Point')  # Increase the marker size for visibility
    ax.legend()
    ax.set_title("Real-Time Anomaly Detection")
    canvas.draw()
    
    # Log and display the anomaly if detected
    if anomaly_detected:
        log_entry = f"Anomaly detected at {ds}: Actual={actual}, Forecast={forecasted}"
        print(log_entry)  # Debug: Print the anomaly log entry
        anomaly_log.append(log_entry)
        with open('anomaly_log.csv', 'a') as f:
            f.write(f"{ds},{actual},{forecasted}\n")
    
    # Update the anomaly listbox
    anomaly_listbox.delete(0, tk.END)
    for entry in anomaly_log:
        anomaly_listbox.insert(tk.END, entry)
    
    # Schedule the next update
    root.after(5000, update_graph)  # Update every 5 seconds

# GUI Setup
root = tk.Tk()
root.title("Real-Time Cloud Cost Anomaly Detection")

# Step 1: Load historical cloud cost data
file_path = r'./SRC/Data/Prophet/RealTimeCloudCostAnomalyDetection.csv'
df = pd.read_csv(file_path)

# Step 2: Convert 'usage_end_time' to datetime
df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

# Step 3: Filter out the last few data points to avoid the dip
df_aggregated = df.groupby('usage_end_time')['cost'].sum().reset_index()
df_aggregated = df_aggregated.iloc[:-3]  # Exclude the last 3 data points

# Step 4: Rename columns for Prophet
df_aggregated.rename(columns={'usage_end_time': 'ds', 'cost': 'y'}, inplace=True)

# Initialize anomaly log
anomaly_log = []

# Create a figure and axis for the plot
fig, ax = plt.subplots(figsize=(10, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Anomaly listbox
anomaly_listbox = tk.Listbox(root, height=10)
anomaly_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Start the real-time update loop
root.after(1000, update_graph)  # Start after 1 second

# Start the Tkinter event loop
root.mainloop()
