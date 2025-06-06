import streamlit as st
from databricks import sql
import os
from datetime import datetime

# Databricks connection setup
def get_databricks_connection():
    return sql.connect(
        server_hostname=os.getenv("DATABRICKS_HOST"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN")
    )

# Form for data collection
with st.form("data_entry_form", clear_on_submit=False):
    st.header("Data Entry Form")
    
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    age = st.number_input("Age", min_value=0, max_value=120)
    signup_date = st.date_input("Signup Date")
    subscription_type = st.selectbox(
        "Subscription Plan",
        ["Free", "Basic", "Premium"]
    )
    
    submitted = st.form_submit_button("Submit to Delta Table")
    
    if submitted:
        # Create DataFrame from form data
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "timestamp": [current_time],
            "name": [name],
            "email": [email],
            "age": [age],
            "signup_date": [signup_date.strftime("%Y-%m-%d")],
            "subscription_type": [subscription_type]
        }
        
        # Insert into Databricks Delta table
        try:
            with get_databricks_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        INSERT INTO default.user_data (timestamp, name, email, age, signup_date, subscription_type)
                        VALUES ('{current_time}', '{name}', '{email}', {age}, 
                                '{signup_date}', '{subscription_type}')
                    """)
                    connection.commit()
            st.success("Data successfully written to Delta table!")
        except Exception as e:
            st.error(f"Error writing to Delta table: {str(e)}")


pip install streamlit databricks-sql-connector python-dotenv

CREATE TABLE default.user_data (
  timestamp TIMESTAMP,
  name STRING,
  email STRING,
  age INT,
  signup_date DATE,
  subscription_type STRING
) USING DELTA;
