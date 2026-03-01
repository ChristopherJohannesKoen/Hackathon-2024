import pandas as pd

data = pd.read_csv("./SRC/data/gcp_billing_data_20240816 - gcp_billing_data_20240816.csv")
fields = data["service_type"].unique()
# for name in fields:
#     mytemp = data[["usage_end_time","cost","usage_amount",(data["usage_unit"] == name)]]
#     ##CHANGES TO HELP VISUALISE/WORK WITH DATA
#     # if len(names) == 1:
#     #     print(name)
#     # print(names)
#     # if name == "Cloud Pub/Sub":
#     #     path = "./SRC/data/split_data/Cloud Pub-Sub.csv"
#     # else:
#     path = "./SRC/data/split_data/_test" + name + ".csv" 
#     mytemp.to_csv(path)
print(fields)