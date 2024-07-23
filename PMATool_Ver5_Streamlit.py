import streamlit as st
import pandas as pd
import numpy as np

# Constants
INTERNAL_AUDIENCE_SIZE_FILE = 'seed_to_audience_per_1k.csv'  #  internal CSV file

# Load internal audience sizes file
def load_file(INTERNAL_AUDIENCE_SIZE_FILE):
    try:
        data = pd.read_csv(file_path)
        st.write("Column names in the internal file:", data.columns.tolist())  # Display column names for debugging, just in case
        return data
    except Exception as e:
        st.error(f"Failed to load internal data: {str(e)}")
        return None

# Validate number input, making sure the number is a integer, no commas
def validate_number(number_str):
    try:
        number = int(number_str.replace(",", ""))
        return True, number
    except ValueError:
        return False, None

def find_closest_audience_size(data, seed_size, tolerance=0.05):  # 5% tolerance by default
    # Convert seed_size to integer if it's input as a string with commas
    seed_size = int(seed_size.replace(',', '')) if isinstance(seed_size, str) else seed_size
    
    # Convert data columns to integer for proper calculation
    data['APROX_EXPORT_SIZE'] = data['APROX_EXPORT_SIZE'].str.replace(',', '').astype(int)
    data['SEED_SIZE'] = data['SEED_SIZE'].str.replace(',', '').astype(int)
    
    # Calculate the percent difference between each seed size and the input seed size
    data['Percent Difference'] = abs(data['SEED_SIZE'] - seed_size) / seed_size
    
    # Find the index of the smallest percent difference that is within the tolerance
    closest_size_index = data[data['Percent Difference'] <= tolerance]['Percent Difference'].idxmin()
    
    # Check if a closest size was found within the tolerance
    if pd.notna(closest_size_index):
        closest_size = data.loc[closest_size_index, 'APROX_EXPORT_SIZE']
        return closest_size
    else:
        # If no size is within the tolerance, return the closest size ignoring the tolerance
        closest_size_index = data['Percent Difference'].idxmin()
        return data.loc[closest_size_index, 'APROX_EXPORT_SIZE']



def find_threshold(dry_run_data, closest_size, tolerance=0.05):  # 5% tolerance by default
    # Ensure cumulative_sum is converted to a float and the Rounded Cumulative Sum is calculated
    dry_run_data['cumulative_sum'] = dry_run_data['cumulative_sum'].astype(float)

    # Calculate the percent difference between each cumulative_sum and the closest_size
    dry_run_data['Percent Difference'] = abs(dry_run_data['cumulative_sum'] - closest_size) / closest_size
    
    # Find the index of the smallest percent difference that is within the tolerance
    valid_indices = dry_run_data['Percent Difference'] <= tolerance
    if valid_indices.any():  # Check if there's any entry within the tolerance
        closest_row_index = dry_run_data.loc[valid_indices, 'Percent Difference'].idxmin()
    else:
        # If no entry is within the tolerance, find the closest one ignoring the tolerance
        closest_row_index = dry_run_data['Percent Difference'].idxmin()
    
    # Return the threshold of the closest row
    threshold = dry_run_data.loc[closest_row_index, 'threshold']
    return threshold





# Function to fetch related rows from audience stats based on threshold
def fetch_stats(audience_stats_data, threshold):
    stats = audience_stats_data[audience_stats_data['SCORE_THRESHOLD'] == threshold]
    idx = stats.index[0]
    return audience_stats_data.loc[idx-2:idx+2]  # Include two rows above and below the matched row


#Streamlit interface
def app():
    st.title('Audience Analysis Tool')
#Upload files gotten from PMA process 
    with st.form("Input_Form"):
        uploaded_dry_run = st.file_uploader("Upload the Dry Run CSV File", key="dry_run")
        uploaded_audience_stats = st.file_uploader("Upload the Audience Stats CSV File", key="audience_stats")
        seed_size_input = st.text_input("Enter Cohort Seed Size:")
        submit_button = st.form_submit_button("Submit")
#After submit is hit, run all the functions defined and return the resulting rows
    if submit_button:
        if uploaded_dry_run and uploaded_audience_stats and seed_size_input:
            dry_run_data = pd.read_csv(uploaded_dry_run)
            audience_stats_data = pd.read_csv(uploaded_audience_stats)
            valid, seed_size = validate_number(seed_size_input)
            if valid:
                audience_data = load_file('pma_seedSize_audienceSize.csv')
                closest_audience_size = find_closest_audience_size(audience_data, seed_size)
                threshold = find_threshold(dry_run_data, closest_audience_size)
                if threshold:
                    related_stats = fetch_stats(audience_stats_data, threshold)
                    if not related_stats.empty:
                        st.session_state['related_stats'] = related_stats
                        st.session_state['audience_stats_data'] = audience_stats_data
                        st.write("Matched Data:",threshold,  related_stats)
                    else:
                        st.error("No matching threshold found in Audience Stats data.")
                else:
                    st.error("No matching audience size found in Dry Run data.")
            else:
                st.error("Invalid cohort seed size. Please enter a valid number.")
        else:
            st.error("Please upload all required files and enter a cohort seed size.")

    # Separate section for filtering the data manually without causing a form resubmission
    if 'audience_stats_data' in st.session_state:
        st.write("### Explore Audience Stats")
        filter_column = st.selectbox("Select column to filter by:", st.session_state['audience_stats_data'].columns)
        filter_query = st.text_input("Enter query (e.g., > 20, == 30, etc.):")
        if st.button("Apply Filter"):
            filtered_data = st.session_state['audience_stats_data'].query(f"`{filter_column}` {filter_query}")
            st.dataframe(filtered_data)

   #JIRA Output (Need to automate):
    st.subheader("JIRA Outputs")
    st.write(" Audience size:###,Threshold: ###, Model power index: ### , AQ score: ### , Cohort seed size: ###. ")

if __name__ == "__main__":
    app()