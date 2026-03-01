import pandas as pd
import matplotlib.pyplot as plt
import os

dir = "./data"

for fileOrDir in os.listdir(dir):
    if(os.path.isfile(f"{dir}/{fileOrDir}")):
        # Load the data
        df = pd.read_csv(f"{dir}/{fileOrDir}")

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
        no_extention = fileOrDir.removesuffix(".csv")
        plt.savefig(f"./plots/{no_extention}")
        plt.clf()
    else:
        fig, axs = plt.subplots(len(os.listdir(f"{dir}/{fileOrDir}")), 1, figsize=(10, 6))
        i = 0
        for file in os.listdir(f"{dir}/{fileOrDir}"):

            # Load the data
            df = pd.read_csv(f"{dir}/{fileOrDir}/{file}")

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

            no_extention = file.removesuffix(".csv")
   
            # Plot the data
            daily_avg_cost_per_hour.plot(kind='bar', ax=axs[i])
            axs[i].set_xlabel('Hour of the Day')
            axs[i].set_ylabel('Average Daily Cost')
            axs[i].set_title(f'Average Daily Cost per Hour for units measured in {no_extention}')

            i += 1
        if(fileOrDir == "Networking"):  
            print(f"0: {axs[0]}, 1: {axs[1]}")
        plt.tight_layout()
        fig.savefig(f"./plots/{fileOrDir}")
        plt.clf()


