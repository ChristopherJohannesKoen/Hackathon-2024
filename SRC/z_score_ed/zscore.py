import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plot

def addZscore(path):
    df = pd.read_csv(path)
    c = 10
    n = len(df) / c
    fin = []
    
    for i in range(1, c + 1):
        pre = int(n * (i - 1))
        post = int(n * i)
        temp = df.iloc[pre:post]
        z = np.array(temp["usage_amount"])
        zstat = list(stats.zscore(z))
        fin.extend(zstat)
    
    # Initialize the MinMaxScaler and normalize z-scores
    scaler = MinMaxScaler()
    normalized_z_scores = scaler.fit_transform(np.array(fin).reshape(-1, 1))

    # Insert only the normalized z-scores into the DataFrame
    df.insert(4, "normalized_z_score", normalized_z_scores)

    # Save the modified DataFrame back to the CSV file
    df.to_csv(path, index=False)