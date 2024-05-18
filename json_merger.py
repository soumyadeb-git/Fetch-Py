import os
import json

def load_json(file_path):
    """ Load JSON data from a file. """
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(file_path, data):
    """ Save JSON data to a file. """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def clean_data(data):
    """ Remove 'Last Fetch Time' tag from data. """
    for item in data:
        if 'Last Fetch Time' in item:
            del item['Last Fetch Time']
    return data

def merge_and_update_json(file1, file2, merged_file):
    # Load and clean data from the first file
    data1 = clean_data(load_json(file1))
    
    # Load and clean data from the second file
    data2 = clean_data(load_json(file2))
    
    # Merge data, preserving unique items
    merged_data = data2 + [item for item in data1 if item not in data2]
    
    # Write merged data to the new JSON file
    save_json(merged_file, merged_data)

# Get list of existing JSON files in the data folder
data_folder = 'data'
files = sorted([f for f in os.listdir(data_folder) if f.endswith('.json')])
file1, file2 = os.path.join(data_folder, files[-2]), os.path.join(data_folder, files[-1])
merged_file = os.path.join(data_folder, f'data{len(files)}.json')

# Merge and update JSON files
merge_and_update_json(file1, file2, merged_file)
