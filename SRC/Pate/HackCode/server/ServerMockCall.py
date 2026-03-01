# import sys
# import os

# # Add the directory to sys.path
# script_directory = r".\server"
# sys.path.append(script_directory)

# from PateIsoTree4V1PointUpdateFile import UpdateFile

# from PateIsoTree4V1PointExtractLast96Hours import EL96H

# # Import the CRADRM function from the script
# from PateStandardDef4V4HourlySumCallReceivedAccessingData import CRADRM

# # # Assuming the CRADRM function is defined in your code
# if __name__ == "__main__":
# #     # Mock received_id and value for testing

    

#     received_id = "4"  # This corresponds to "Cloud Storage" in the id.json
#     value = 0.18  # An example value that may be an anomaly

#     # Call the CRADRM function with the mock data
#     CRADRM(received_id)

#     #L96H(received_id)

#     #UpdateFile(received_id, 5)

import sys
import os

# Add the directory to sys.path
script_directory = r".\server"
sys.path.append(script_directory)

from PateIsoTree4V1PointUpdateFile import UpdateFile
from PateIsoTree4V1PointExtractLast96Hours import EL96H
from PateIsoTree4V1PointCallReceivedAccessingData import CRADRM

# Dictionary mapping IDs to service names
id_mapping = {
    "1": "Networking",
    "2": "Cloud Logging",
    "3": "Kubernetes Engine",
    "4": "Cloud Storage",
    "5": "BigQuery",
    "6": "Vertex AI",
    "7": "Cloud Monitoring",
    "8": "Cloud SQL",
    "9": "Cloud DNS",
    "10": "Cloud Pub/Sub",
    "11": "Artifact Registry",
    "12": "Cloud Functions",
    "13": "Cloud Build",
    "14": "BigQuery Reservation API",
    "15": "Deep Learning VM",
    "16": "Cloud Dataflow",
    "17": "Dataplex"
}

# Main block
if __name__ == "__main__":
    # Loop through all IDs in the id_mapping
    for received_id in id_mapping.keys():
        print(f"Processing ID: {received_id} - {id_mapping[received_id]}")
        
        # Example value; replace with your own logic if needed
        value = 0.18

        # Call the CRADRM function with the current ID
        CRADRM("1")

        # You can also call the UpdateFile or EL96H functions if needed
        # UpdateFile(received_id, value)
        # EL96H(received_id)

    print("Processing completed for all IDs.")
