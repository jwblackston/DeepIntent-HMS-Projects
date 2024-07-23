import streamlit as st
import pandas as pd

# Constants
threshold_3x = 0.000512  # Replace with the actual value

# Load file
def load_file(file):
    if file is not None:
        data = pd.read_csv(file)
        return data
    return None

# Validate number
def validate_number(number_str):
    number_str = number_str.replace(",", "")
    if number_str.isdigit():
        number = int(number_str)
        if 40000 <= number <= 30000000:
            return True
    return False

# Analyze data
def analyze(data, cohort_seed_size):
    try:
        cohort_seed_size = int(cohort_seed_size.replace(",", ""))
        cohort_seed_size_result = cohort_seed_size * 5 / 2
        closest_index = (data['AUDIENCE_SIZE'] - cohort_seed_size_result).abs().idxmin()
        closest_row = data.loc[closest_index]
        
        score_threshold = closest_row['SCORE_THRESHOLD']
        audience_stat_size = closest_row['AUDIENCE_SIZE']
        aq_score = closest_row['AQ_SCORE']
        model_power_index = closest_row['MODEL_POWER_INDEX']
        seed_size = cohort_seed_size

        return {
            "SCORE_THRESHOLD": score_threshold,
            "AUDIENCE_STAT_SIZE": {cohort_seed_size_result},
            "AQ_SCORE": aq_score,
            "THRESHOLD_3X": threshold_3x,
            "MODEL_POWER_INDEX": model_power_index,
	    "SEED_SIZE": cohort_seed_size
        }
    except Exception as e:
        return f"Error in processing data: {str(e)}"

# Streamlit UI components
st.title('Audience Stats Analyzer')

uploaded_file = st.file_uploader("Choose a file (CSV format)")
if uploaded_file is not None:
    data = load_file(uploaded_file)
    if data is not None:
        st.write(data.head())  # Display first few rows of the dataframe
        cohort_seed_size = st.text_input("Enter Cohort Seed Size (40,000 - 30,000,000):")
        
        if st.button("Analyze"):
            if validate_number(cohort_seed_size):
                result = analyze(data, cohort_seed_size)
                if isinstance(result, dict):
                    st.write(result)
                else:
                    st.error(result)
            else:
                st.error("Invalid cohort seed size. Please enter a number between 40,000 and 30,000,000.")

