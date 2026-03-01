import pandas as pd
import json
import os
import shutil

# Load CSV data into a DataFrame
df = pd.read_csv("./bigData.csv")

# Get unique service types
unique = df["service_type"].unique()

# Create index dictionaries for service types
indexed_dict = {index: name for index, name in enumerate(unique)}
index_invers = {name: index for index, name in enumerate(unique)}

# Define paths to save JSON files
file_name1 = './ids.json'
file_name2 = './services.json'

if os.path.exists(file_name1):
    os.remove(file_name1)

if os.path.exists(file_name2):
    os.remove(file_name2)

if os.path.exists('./runTimeData'):
    shutil.rmtree('./runTimeData')


if not os.path.exists('./runTimeData'):
    os.makedirs('./runTimeData')

# Save indexed dictionaries as JSON files
with open(file_name1, 'w') as json_file:
    json.dump(indexed_dict, json_file)
with open(file_name2, 'w') as json_file:
    json.dump(index_invers, json_file)

# Iterate over unique service types and save CSV files
for name in unique:
    # Filter data for each service type
    temp1 = df[df["service_type"] == name]
    
    # Subset relevant columns
    mytemp = temp1[["usage_end_time", "cost", "usage_amount", "usage_unit", "service_type"]]
    
    # Create a path for saving files based on the service type
    path = "./runTimeData/" + str(name)
    
    # Check if the directory exists, if not create it
    if not os.path.exists(path):
        os.makedirs(path)
    
    # Determine file name and save CSV
    mytemp.to_csv(os.path.join(path,"data.csv"), index=False)
