import streamlit as st
import pandas as pd
import mysql.connector
from pyspark.sql import SparkSession
import os
from dotenv import load_dotenv



#Loading Credentials from env file
load_dotenv()
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
JDBC_URL = os.getenv("JDBC_URL")
JDBC_DRIVER = os.getenv("JDBC_DRIVER")
JDBC_USER = os.getenv("JDBC_USER")
JDBC_PASSWORD = os.getenv("JDBC_PASSWORD")


# Constants
INTERNAL_AUDIENCE_SIZE_FILE = 'seed_to_audience_per_1k.csv'  # Internal CSV file
#Hello testing testing Hello world


# Function to create a connection to the MySQL database
def create_connection( user, password):
    return mysql.connector.connect(
        host= MYSQL_HOST,
        user= MYSQL_USER,
        password= MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

# Function to fetch data from the database
def fetch_data(query, user, password,):
    conn = create_connection(user, password,)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [i[0] for i in cursor.description]
    cursor.close()
    conn.close()
    return pd.DataFrame(rows, columns=columns)


def create_spark_session():
    spark = SparkSession.builder \
        .appName("Streamlit Spark Connection") \
        .getOrCreate()

    # Set JDBC properties
    properties = {
        "user": JDBC_USER,
        "password": JDBC_PASSWORD,
        "driver": JDBC_DRIVER
    }

    return spark, properties


# Function to validate number input, making sure the number is an integer without commas
def validate_number(number_str):
    try:
        number = int(number_str.replace(",", ""))
        return True, number
    except ValueError:
        return False, None

# Function to load a CSV file and display column names for debugging
def load_file(file_path):
    try:
        data = pd.read_csv(file_path)
        st.write("Column names in the internal file:", data.columns.tolist())
        return data
    except Exception as e:
        st.error(f"Failed to load internal data: {str(e)}")
        return None

# Function to find the closest audience size
def find_closest_audience_size(data, seed_size, tolerance=0.05):  # 5% tolerance by default
    seed_size = int(seed_size.replace(',', '')) if isinstance(seed_size, str) else seed_size
    data['AUDIENCE SIZE APROX'] = data['AUDIENCE SIZE APROX'].str.replace(',', '').astype(int)
    data['SEED SIZE'] = data['SEED SIZE'].str.replace(',', '').astype(int)
    data['Percent Difference'] = abs(data['SEED SIZE'] - seed_size) / seed_size
    closest_size_index = data[data['Percent Difference'] <= tolerance]['Percent Difference'].idxmin()
    if pd.notna(closest_size_index):
        closest_size = data.loc[closest_size_index, 'AUDIENCE SIZE APROX']
        return closest_size
    else:
        closest_size_index = data['Percent Difference'].idxmin()
        return data.loc[closest_size_index, 'AUDIENCE SIZE APROX']

# Function to find the threshold
def find_threshold(dry_run_data, closest_size, tolerance=0.05):  # 5% tolerance by default
    dry_run_data['cumulative_sum'] = dry_run_data['cumulative_sum'].astype(float)
    dry_run_data['Percent Difference'] = abs(dry_run_data['cumulative_sum'] - closest_size) / closest_size
    valid_indices = dry_run_data['Percent Difference'] <= tolerance
    if valid_indices.any():
        closest_row_index = dry_run_data.loc[valid_indices, 'Percent Difference'].idxmin()
    else:
        closest_row_index = dry_run_data['Percent Difference'].idxmin()
    threshold = dry_run_data.loc[closest_row_index, 'threshold']
    return threshold

# Function to get cumulative sum
def get_cumsum(dry_run_data, closest_size, tolerance=0.05):
    dry_run_data['cumulative_sum'] = dry_run_data['cumulative_sum'].astype(float)
    dry_run_data['Percent Difference'] = abs(dry_run_data['cumulative_sum'] - closest_size) / closest_size
    valid_indices = dry_run_data['Percent Difference'] <= tolerance
    if valid_indices.any():
        closest_row_index = dry_run_data.loc[valid_indices, 'Percent Difference'].idxmin()
    else:
        closest_row_index = dry_run_data['Percent Difference'].idxmin()
    cum_sum = dry_run_data.loc[closest_row_index, 'cumulative_sum']
    return cum_sum

# Function to fetch related rows from audience stats based on threshold
def fetch_stats(audience_stats_data, threshold):
    stats = audience_stats_data[audience_stats_data['SCORE_THRESHOLD'] == threshold]
    idx = stats.index[0]
    st.session_state['idx'] = idx
    return audience_stats_data.loc[idx-2:idx+2]  # Include two rows above and below the matched row

def app():
    st.title('Audience Analysis Tool')

    with st.form("Input_Form"):
        seed_size_input = st.text_input("Enter Cohort Seed Size:")
        submit_button = st.form_submit_button("Submit")


    if submit_button:
        if seed_size_input:
            valid, seed_size = validate_number(seed_size_input)
            if valid:
                # SQL query to fetch Dry Run data
                query = """
                SELECT 
                    threshold, 
                    percentile_sum, 
                    cumulative_sum
                FROM bidder.AUDIENCE_MODEL am 
                CROSS JOIN JSON_TABLE(dryrunResults, '$[*]'
                    COLUMNS (
                        threshold DOUBLE PATH '$.threshold',
                        `percentile_sum` INT PATH '$."percentile sum"',
                        `cumulative_sum` BIGINT PATH '$."cumulative sum"'
                    )
                ) AS jt
                WHERE patientModelId = 13635; 
                """

                #Spark query to fetch Dry Run data
                query2 = """
                SELECT
                    SCORE_THRESHOLD,	
                    AUDIENCE_SIZE,	
                    VERIFIED_PATIENTS,	
                    AQ_SCORE,	
                    INCREMENTAL_AQ_SCORE,	
                    PERCENT_POPULATION, 
                    PERCENT_PATIENTS,	
                    THRESHOLD_3X,	
                    PREVALENCE, 
                    MODEL_POWER_INDEX,
                    TRUE_POSITIVE, 
                    FALSE_POSITIVE, 
                    TRUE_NEGATIVE, 
                    FALSE_NEGATIVE
                FROM pma.pma_sentinel_metrics
                WHERE train_id like '1714131589017'
                AND score_threshold = 0.0648
                ORDER BY score_threshold DESC 
                """

                spark, properties = create_spark_session()

                dry_run_data = fetch_data(query, user, password)

                audience_stats_data = pd.read_csv(uploaded_audience_stats)
                audience_stats_data = fetch_spark_data(spark, query2, properties).toPandas()

                if dry_run_data.empty:
                    st.error("No Dry Run data found.")
                else:
                    st.write("Dry Run Data Loaded", dry_run_data)

                if not audience_stats_data.empty:
                    st.write("Audience Stats Data Loaded", audience_stats_data)
                else:
                    st.error("Failed to load Audience Stats data.")

                audience_data = load_file(INTERNAL_AUDIENCE_SIZE_FILE)
                closest_audience_size = find_closest_audience_size(audience_data, seed_size)
                threshold = find_threshold(dry_run_data, closest_audience_size)
                cum_sum = int(get_cumsum(dry_run_data, closest_audience_size))
                if threshold:
                    related_stats = fetch_stats(audience_stats_data, threshold)
                    if not related_stats.empty:
                        st.session_state['related_stats'] = related_stats
                        st.session_state['audience_stats_data'] = audience_stats_data
                        st.write("Matched Data:", threshold, related_stats)
                    if 'audience_stats_data' in st.session_state:
                        maxAQ = audience_stats_data['AQ_SCORE'].iloc[0]
                        maxModelP = audience_stats_data['MODEL_POWER_INDEX'].iloc[0]
                        st.write(f"### Max AQ: {maxAQ} and Max Model Power: {maxModelP}")
                    # JIRA Output:
                    if 'related_stats' in st.session_state:
                        st.subheader("JIRA Outputs")
                        aq_score = st.session_state['related_stats']['AQ_SCORE'].iloc[2]
                        model_power = st.session_state['related_stats']['MODEL_POWER_INDEX'].iloc[2]
                        st.write(f"Audience size: {cum_sum}, \n\n Threshold: {threshold},\n\n Model power index: {model_power}, \n\nAQ score: {aq_score}, \n\n Cohort seed size: {seed_size}.")
                    else:
                        st.error("No matching threshold found in Audience Stats data.")
                else:
                    st.error("No matching audience size found in Dry Run data.")
            else:
                st.error("Invalid cohort seed size. Please enter a valid number.")
        else:
            st.error("Please fill in all required fields and upload the necessary files.")

    # Separate section for filtering without causing a form resubmission
    if 'audience_stats_data' in st.session_state:
        st.write("### Explore Audience Stats")
        filter_column = st.selectbox("Select column to filter by:", st.session_state['audience_stats_data'].columns)
        filter_query = st.text_input("Enter query (e.g., > 20, == 30, etc.):")
        if st.button("Apply Filter"):
            filtered_data = st.session_state['audience_stats_data'].query(f"`{filter_column}` {filter_query}")
            st.dataframe(filtered_data)

if __name__ == "__main__":
    app()


# % streamlit run 'PMATool_Streamlit_WITH_SQL_DONTSHARE.py' --server.maxMessageSize 400

