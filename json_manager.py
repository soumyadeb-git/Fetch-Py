import os
import json

def merge_and_update_json(file1, file2, merged_file):
    # Load data from the first file
    with open(file1, 'r') as f1:
        data1 = json.load(f1)

    # Load data from the second file
    with open(file2, 'r') as f2:
        data2 = json.load(f2)

    # Merge and update data
    merged_data = data2 + [item for item in data1 if item not in data2]

    # Write merged data to new JSON file
    with open(merged_file, 'w') as f:
        json.dump(merged_data, f, indent=4)

# File paths
data_folder = 'data'
file1 = os.path.join(data_folder, 'data1.json')
file2 = os.path.join(data_folder, 'data2.json')
merged_file = os.path.join(data_folder, 'merged_data.json')

# Merge and update JSON files
merge_and_update_json(file1, file2, merged_file)
