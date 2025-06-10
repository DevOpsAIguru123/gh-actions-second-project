import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()  # Set the DATABRICKS_HOST environment variable when running locally

# Permanent variables for connection
HTTP_PATH = "/sql/1.0/warehouses/f3de4cf2e0a0683c"
TABLE_NAME = "dbxappscatalog.demo_schema.demo_usecase_tracker"

def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def create_table(conn):
    with conn.cursor() as cursor:
        # Drop table if exists
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        
        # Create the new table with env_needed as VARCHAR
        create_table_sql = f"""
        CREATE TABLE {TABLE_NAME} (
            env_needed VARCHAR(255),
            usercase_name VARCHAR(255),
            key_contact VARCHAR(255),
            L2 VARCHAR(255),
            BL VARCHAR(100),
            support_type VARCHAR(100),
            sub VARCHAR(100),
            ads VARCHAR(100),
            sps VARCHAR(100),
            data_connections STRING,
            started_provision_access_on DATE,
            support_finished_on DATE,
            current_stage VARCHAR(100),
            l2_costcenter VARCHAR(100),
            note STRING
        )
        """
        cursor.execute(create_table_sql)
        st.success(f"✅ Table {TABLE_NAME} created successfully!")

st.title("Create Use Case Tracker Table")

if st.button("Create Table"):
    conn = get_connection(HTTP_PATH)
    create_table(conn)
