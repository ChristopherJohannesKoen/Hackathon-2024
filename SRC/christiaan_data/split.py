import pandas as pd
import os

df = pd.read_csv("original_data.csv")

df_grouped = df.groupby("service_type")

for service_type, group in df_grouped:
    service_type = service_type.replace("/", "-")
    temp_groups = group.groupby("usage_unit")
    if(len(temp_groups) > 1):
        dir = f"./data/{service_type}"

        if not os.path.exists(dir):
            os.makedirs(dir)

        for usage_unit, unitGroup in temp_groups:
            unitGroup.to_csv(f"{dir}/{service_type}_{usage_unit}.csv")
    else:
        dir = f"./data"
        if not os.path.exists(dir):
            os.makedirs(dir)
        group.to_csv(f"{dir}/{service_type}.csv")