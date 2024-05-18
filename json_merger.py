import os
import json

def remove_last_fetch_time(data):
    """Remove 'Last Fetch Time' from each item in the list."""
    for item in data:
        item.pop('Last Fetch Time', None)
    return data

def merge_and_update_json(file1, file2, merged_file, key='Title'):
    """Merge two JSON files, remove 'Last Fetch Time' tags, and save the result."""
    # Load data from the first file
    with open(file1, 'r') as f1:
        data1 = json.load(f1)
        data1 = remove_last_fetch_time(data1)

    # Load data from the second file
    with open(file2, 'r') as f2:
        data2 = json.load(f2)
        data2 = remove_last_fetch_time(data2)

    # Create a dictionary to store items by key (Title)
    merged_dict = {}

    def add_or_update_item(item):
        """Add or update item in the merged_dict."""
        item_key = item.get(key)
        if item_key is not None:
            # Update existing item or add new one based on Title
            merged_dict[item_key] = item

    # Add items from the first file to the dictionary
    for item in data1:
        add_or_update_item(item)

    # Update or add items from the second file
    for item in data2:
        add_or_update_item(item)

    # Convert the dictionary back to a list
    merged_data = list(merged_dict.values())

    # Write merged data to new JSON file
    with open(merged_file, 'w') as f:
        json.dump(merged_data, f, indent=4)
        print(f"Data written to {merged_file}")

# File paths
data_folder = 'data'
file1 = os.path.join(data_folder, 'data1.json')
file2 = os.path.join(data_folder, 'data2.json')
merged_file = os.path.join(data_folder, 'merged_data.json')

# Merge and update JSON files
merge_and_update_json(file1, file2, merged_file)
