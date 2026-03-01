import matplotlib.pyplot as plt
import pandas as pd
import os

directory = "./data"



plt.xlabel("Time")
plt.ylabel("Cost")
for file in os.listdir(directory):
    name = file.removesuffix(".csv")
    df = pd.read_csv(f"./data/{file}")

    plt.figure(figsize=(df.shape[1] * 10, df.shape[1] * 2), dpi=100)

    plt.plot(df.usage_end_time, df.cost, linewidth=0.25)
    
    plt.title(f"Cost over time for {name}")

    plt.savefig(f"./plots/{name}.jpg")
