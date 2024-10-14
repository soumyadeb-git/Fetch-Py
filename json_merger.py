import os
import json
from datetime import datetime

def remove_last_fetch_time(data):
    """Remove 'Last Fetch Time' from each item in the list."""
    for item in data:
        item.pop('Last Fetch Time', None)
    return data

def get_today_str():
    """Get today's date as a formatted string."""
    return datetime.now().strftime('%B %d, %Y')

def load_json_file(file_path):
    """Load a JSON file, return an empty list if the file is empty or not valid."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []  # Return an empty list if the file does not exist or is empty

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}. Returning an empty list.")
        return []  # Return an empty list if there's a JSON decoding error

def filter_and_merge_data(data1, data2):
    """Filter data based on today's date and merge both datasets."""
    today_str = get_today_str()

    # Create a dictionary to hold the most recent entries
    merged_dict = {}

    # Process first dataset
    for item in data1:
        item_key = item.get('Title')
        if item_key:
            merged_dict[item_key] = item  # Add or update entry

    # Process second dataset
    for item in data2:
        item_key = item.get('Title')
        if item_key:
            # If the item is already in the dictionary, check if it should be updated
            if item_key in merged_dict:
                existing_item_date = merged_dict[item_key]['Updated On']
                new_item_date = item['Updated On']
                # Only keep the most recent item
                if new_item_date > existing_item_date:
                    merged_dict[item_key] = item
            else:
                merged_dict[item_key] = item  # Add new entry

    # Sort data by 'Updated On' date, giving priority to today's data
    merged_data = list(merged_dict.values())
    merged_data.sort(key=lambda x: (x.get('Updated On') != today_str, x.get('Updated On')), reverse=True)

    return merged_data

def merge_and_update_json(file1, file2, merged_file):
    """Merge two JSON files, remove 'Last Fetch Time' tags, and save the result."""
    # Load data from the first file
    data1 = load_json_file(file1)
    data1 = remove_last_fetch_time(data1)

    # Load data from the second file
    data2 = load_json_file(file2)
    data2 = remove_last_fetch_time(data2)

    # Filter and merge data
    merged_data = filter_and_merge_data(data1, data2)

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
