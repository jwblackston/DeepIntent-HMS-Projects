import pandas as pd
import numpy as np

# Constants
INTERNAL_AUDIENCE_SIZE_FILE = 'pma_seedSize_audienceSize.csv'  # Path to internal file with audience sizes

# Load internal audience sizes file
def load_file():
    try:
        data = pd.read_csv(INTERNAL_AUDIENCE_SIZE_FILE)
        return data
    except Exception as e:
        print(f"Failed to load internal data: {str(e)}")
        return None

# Validate number input
def validate_number(number_str):
    try:
        number = int(number_str.replace(",", ""))
        return True, number
    except ValueError:
        return False, None

def find_closest_audience_size(data, seed_size):
    # Round the seed size to the nearest 10K
    rounded_seed_size = round(seed_size / 10000) * 10000
    
    # Calculate the difference between each audience size and the rounded seed size
    data['Difference'] = abs(data['SEED SIZE'] - rounded_seed_size)
    
    # Find the index of the minimum difference
    closest_size_index = data['Difference'].idxmin()
    
    # Return the approximate export size that is closest to the rounded seed size
    closest_size = data.loc[closest_size_index, 'APROX EXPORT SIZE']
    return closest_size

# Find matching threshold in dry run data
def find_threshold(dry_run_data, audience_size):
    dry_run_data['Rounded Cumulative Sum'] = dry_run_data['cumulative_sum'].round(-4)  # Round to nearest 10,000
    matched_row = dry_run_data[dry_run_data['Rounded Cumulative Sum'] == round(audience_size, -4)]
    if not matched_row.empty:
        return matched_row.iloc[0]['threshold']
    return None

# Fetch related rows from audience stats based on threshold
def fetch_stats(audience_stats_data, threshold):
    stats = audience_stats_data[audience_stats_data['threshold'] == threshold]
    if not stats.empty:
        idx = stats.index[0]
        return audience_stats_data.loc[idx-2:idx+2]  # Include two rows above and below the matched row
    return None

# Load internal data
internal_data = load_file()

# Input CSV file paths from user
dry_run_file_path = input("Enter the path to the Dry Run CSV File: ")
audience_stats_file_path = input("Enter the path to the Audience Stats CSV File: ")

if internal_data is not None:
    dry_run_data = pd.read_csv(dry_run_file_path)
    audience_stats_data = pd.read_csv(audience_stats_file_path)

    seed_size_input = input("Enter Cohort Seed Size: ")
    valid, seed_size = validate_number(seed_size_input)
    if valid:
        closest_audience_size = find_closest_audience_size(internal_data, seed_size)
        threshold = find_threshold(dry_run_data, closest_audience_size)
        if threshold is not None:
            related_stats = fetch_stats(audience_stats_data, threshold)
            if related_stats is not None:
                print("Matched Data:\n", related_stats)
            else:
                print("No matching threshold found in Audience Stats data.")
        else:
            print("No matching audience size found in Dry Run data.")
    else:
        print("Invalid cohort seed size. Please enter a valid number.")
