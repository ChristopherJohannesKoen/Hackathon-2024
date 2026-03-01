import matplotlib.pyplot as plot
import numpy as np
import scipy.stats as stats
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Read the list of service fields
fields = list(pd.read_csv("./SRC/data/split_data/_Services.csv"))

# Loop through the list of service fields
for i in range(1, len(fields)):
    path = "./SRC/data/split_data/" + fields[i] + ".csv"  # Use the correct index i
    df = pd.read_csv(path)
    
    c = 10
    n = len(df) / c
    z_scores = []

    # Calculate z-scores for each chunk of the data
    for j in range(1, c + 1):
        pre = int(n * (j - 1))
        post = int(n * j)
        temp = df.iloc[pre:post]
        z = np.array(temp["usage_amount"])
        zstat = list(stats.zscore(z))
        z_scores.extend(zstat)  # Collect z-scores for the entire data

    # Insert z-scores into the DataFrame
    df.insert(4, "z_score", z_scores)

    # Initialize the MinMaxScaler
    scaler = MinMaxScaler()

    # Normalize the z_score column
    df['normalized_z_score'] = scaler.fit_transform(df[['z_score']])

    # Plot the data
    figure, axis = plot.subplots(3, 1, figsize=(10, 8))  # Adjusted subplot layout
    x1 = df["usage_end_time"]
    y1 = df["cost"]
    y2 = df["normalized_z_score"]
    y3 = df["usage_amount"]

    axis[0].plot(x1, y1)
    axis[0].set_title("Cost over Time")
    axis[0].set_xlabel("Time")
    axis[0].set_ylabel("Cost")

    axis[1].plot(x1, y2, color="red")
    axis[1].set_title("Normalized Z-Score of Usage Amount over Time")
    axis[1].set_xlabel("Time")
    axis[1].set_ylabel("Normalized Z-Score")

    axis[2].plot(x1, y3)
    axis[2].set_title("Usage Amount over Time")
    axis[2].set_xlabel("Time")
    axis[2].set_ylabel("Usage Amount")

    plot.tight_layout()
    plot.show()
