import pandas as pd
import matplotlib.pyplot as plt

# # Load the CSV file
file_path = './SRC/data/split_data/Compute Engine.csv'
data = pd.read_csv(file_path)

# # Convert the 'usage_end_time' column to datetime
# data['usage_end_time'] = pd.to_datetime(data['usage_end_time'])

# # Group data by service type and time, summing the costs
# grouped_data = data.groupby(['usage_end_time', 'service_type']).sum().reset_index()

# # Pivot the data to have service types as columns
# pivot_data = grouped_data.pivot(index='usage_end_time', columns='service_type', values='cost')

# # Plotting each service type on a separate chart
# service_types = pivot_data.columns
# num_services = len(service_types)

# plt.figure(figsize=(14, num_services * 4))
# for i, service in enumerate(service_types, 1):
#     plt.subplot(num_services, 1, i)
#     plt.plot(pivot_data.index, pivot_data[service], label=service, color='tab:blue')
#     plt.title(f'Cost Over Time for {service}')
#     plt.xlabel('Time')
#     plt.ylabel('Cost (USD)')
#     plt.grid(True)
#     plt.legend()

# plt.tight_layout()
# plt.show()
x = data["usage_end_time"].head(350000)
y1 = data["cost"].head(350000)
plt.plot(x,y1)
manager = plt.get_current_fig_manager()
manager.full_screen_toggle()
plt.show()