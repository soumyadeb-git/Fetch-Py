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

def filter_and_merge_data(data1, data2, data3):
    """Filter data based on today's date and merge three datasets."""
    today_str = get_today_str()

    # Create a dictionary to hold the most recent entries
    merged_dict = {}

    # Process all three datasets
    for item in data1 + data2 + data3:
        item_key = item.get('Title')
        if item_key:
            existing_item = merged_dict.get(item_key)
            if not existing_item or item['Updated On'] > existing_item['Updated On']:
                merged_dict[item_key] = item  # Keep the most recent item

    # Sort data by 'Updated On' date
    merged_data = list(merged_dict.values())
    
    # Create a separate list for today's entries
    today_entries = [item for item in merged_data if item.get('Updated On') == today_str]
    other_entries = [item for item in merged_data if item.get('Updated On') != today_str]

    # Sort the other entries by 'Updated On' date
    other_entries.sort(key=lambda x: x.get('Updated On'), reverse=True)

    # Combine today's entries with other entries
    sorted_data = today_entries + other_entries

    return sorted_data

def merge_and_update_json(file1, file2, file3, merged_file):
    """Merge three JSON files, remove 'Last Fetch Time' tags, and save the result."""
    # Load data from the first file
    data1 = load_json_file(file1)
    data1 = remove_last_fetch_time(data1)

    # Load data from the second file
    data2 = load_json_file(file2)
    data2 = remove_last_fetch_time(data2)

    # Load data from the third file
    data3 = load_json_file(file3)
    data3 = remove_last_fetch_time(data3)

    # Filter and merge data
    merged_data = filter_and_merge_data(data1, data2, data3)

    # Write merged data to new JSON file
    with open(merged_file, 'w') as f:
        json.dump(merged_data, f, indent=4)
        print(f"Data written to {merged_file}")

# File paths
data_folder = 'data'
file1 = os.path.join(data_folder, 'data1.json')
file2 = os.path.join(data_folder, 'data2.json')
file3 = os.path.join(data_folder, 'info.json')  # Add the new file here
merged_file = os.path.join(data_folder, 'merged_data.json')

# Merge and update JSON files
merge_and_update_json(file1, file2, file3, merged_file)
