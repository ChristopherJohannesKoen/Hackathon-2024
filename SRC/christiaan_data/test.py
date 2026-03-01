import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('Networking_seconds.csv')

# Convert usage_end_time to datetime
df['usage_end_time'] = pd.to_datetime(df['usage_end_time'])

# Extract the hour from usage_end_time
df['hour'] = df['usage_end_time'].dt.hour

# Extract the date from usage_end_time
df['date'] = df['usage_end_time'].dt.date

# Group by date and hour, then calculate the average cost
hourly_avg_cost = df.groupby(['date', 'hour'])['cost'].mean().reset_index()

# Group by hour to get the average daily cost for each hour
daily_avg_cost_per_hour = hourly_avg_cost.groupby('hour')['cost'].mean()

# Plot the data
daily_avg_cost_per_hour.plot(kind='bar', figsize=(10, 6))
plt.xlabel('Hour of the Day')
plt.ylabel('Average Daily Cost')
plt.title('Average Daily Cost per Hour')
plt.show()
