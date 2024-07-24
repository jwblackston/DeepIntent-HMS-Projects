import streamlit as st
import pandas as pd
import numpy as np

# Constants
INTERNAL_AUDIENCE_SIZE_FILE = 'pma_seedSize_audienceSize.csv'  #  internal CSV file

# Load internal audience sizes file
def load_file(file_path):
    try:
        data = pd.read_csv(file_path)
        st.write("Column names in the internal file:", data.columns.tolist())  # Display column names for debugging, just in case
        return data
    except Exception as e:
        st.error(f"Failed to load internal data: {str(e)}")
        return None

# Validate number input, making sure the # is a integer no commas
def validate_number(number_str):
    try:
        number = int(number_str.replace(",", ""))
        return True, number
    except ValueError:
        return False, None

def find_closest_audience_size(data, seed_size):
    # Round the seed size to the nearest 10K
    rounded_seed_size = round(seed_size / 10000) * 10000
    # Ensure columns are correctly formatted as integers
    data['APROX_EXPORT_SIZE'] = data['APROX_EXPORT_SIZE'].str.replace(',', '').astype(int)
    data['SEED_SIZE'] = data['SEED_SIZE'].str.replace(',', '').astype(int)
    # Calculate differences and find the closest size
    data['Difference'] = abs(data['SEED_SIZE'] - rounded_seed_size)
    closest_size_index = data['Difference'].idxmin()
    closest_size = data.loc[closest_size_index, 'APROX_EXPORT_SIZE']
    return closest_size


def find_threshold(dry_run_data, closest_size):
    audience_size_rounded = round(closest_size, -4)
    dry_run_data['Difference'] = abs(dry_run_data['cumulative_sum'] - audience_size_rounded)
    
    # Find the index of the minimum difference
    closest_row_index = dry_run_data['Difference'].idxmin()
    
    # Return the threshold of the closest row
    dry_run_data.loc[closest_row_index, 'threshold']
    threshold = dry_run_data.loc[closest_row_index, 'threshold']
    return threshold



# Function to fetch related rows from audience stats based on threshold
def fetch_stats(audience_stats_data, threshold):
    stats = audience_stats_data[audience_stats_data['SCORE_THRESHOLD'] == threshold]
    idx = stats.index[0]
    return audience_stats_data.loc[idx-2:idx+2]  # Include two rows above and below the matched row


# Streamlit UI components
st.title('Audience Analysis Tool')
uploaded_dry_run = st.file_uploader("Upload the Dry Run CSV File", key="dry_run")
uploaded_audience_stats = st.file_uploader("Upload the Audience Stats CSV File", key="audience_stats")
seed_size_input = st.text_input("Enter Cohort Seed Size:")

st.header('Function Descriptions') 

st.subheader('find_closest_audience_size(data, seed_size)')
st.write(' This function takes the seed size, rounds it to the nearest 10k, then looks it up in the PMA seed size csv, then a new column is made that takes the absolute difference [Approx Seed size - Rounded cohort seed size], and returns the Approximate export size from the PMA seed size csv.')

st.subheader('find_threshold(dry_run_data, closest_size)')
st.write('This function takes the approximate audience size, rounds it, then looks it up in the Dry Run stats file, then a new column is made that takes the absolute difference[abs(dry_run_data[cumulative_sum] - audience_size_rounded)], and find that row with the smallest difference. The threshold is then returned. ')

st.subheader('fetch_stats(audience_stats_data, threshold)') 
st.write('This function takes the threshold found from the dry run and matches it exactly in the audience statistics file. The function returns the row with the matched threshold and the 2 above it and the 2 below it.')

if st.button("Calculate Threshold"):
    if uploaded_dry_run and uploaded_audience_stats and seed_size_input:
        dry_run_data = pd.read_csv(uploaded_dry_run)
        audience_stats_data = pd.read_csv(uploaded_audience_stats)
        valid, seed_size = validate_number(seed_size_input)
        if valid:
            # Assuming audience_data is loaded from a file or input as needed
            audience_data = load_file(INTERNAL_AUDIENCE_SIZE_FILE)
            closest_audience_size = find_closest_audience_size(audience_data, seed_size)
            threshold = find_threshold(dry_run_data, closest_audience_size)
            if threshold is not None:
                related_stats = fetch_stats(audience_stats_data, threshold)
                if related_stats is not None:
                    st.write("Matched Data:", related_stats)
                else:
                    st.error("No matching threshold found in Audience Stats data.")
            else:
                st.error("No matching audience size found in Dry Run data.")
        else:
            st.error("Invalid cohort seed size. Please enter a valid number.")
    else:
        st.error("Please upload all required files and enter a cohort seed size.")
