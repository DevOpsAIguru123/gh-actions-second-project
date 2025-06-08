import streamlit as st
from databricks import sql
from databricks.sdk.core import Config
from datetime import datetime


cfg = Config()  # Set the DATABRICKS_HOST environment variable when running locally

# Permanent variables for connection
HTTP_PATH = "/sql/1.0/warehouses/f3de4cf2e0a0683c"
TABLE_NAME = "dbxappscatalog.demo_schema.demo_table"

@st.cache_resource # connection is cached
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name, conn):
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()

def insert_data(table_name, conn, firstname, lastname, dob):
    with conn.cursor() as cursor:
        query = f"""
        INSERT INTO {table_name} (first_name, last_name, dob, inserted_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP())
        """
        cursor.execute(query, [firstname, lastname, dob])
        conn.commit()

# Create a form for user input
with st.form("user_form"):
    firstname = st.text_input("First Name")
    lastname = st.text_input("Last Name")
    dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1))
    
    # Submit button
    submit_button = st.form_submit_button("Submit")

if submit_button and firstname and lastname and dob:
    try:
        conn = get_connection(HTTP_PATH)
        
        # Insert the new data
        insert_data(TABLE_NAME, conn, firstname, lastname, dob)
        st.success("Data successfully inserted!")
        
        # Fetch and display updated data
        df = read_table(TABLE_NAME, conn)
        
        # Add new user data to the displayed dataframe
        st.write("### Table Data:")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    conn = get_connection(HTTP_PATH)
    df = read_table(TABLE_NAME, conn)
    st.dataframe(df)