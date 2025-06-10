import streamlit as st
from databricks import sql
from databricks.sdk.core import Config
from datetime import datetime

# Set page title and configuration - Must be the first Streamlit command
st.set_page_config(
    page_title="Use Case Tracker",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to make the app look better
st.markdown("""
    <style>
    /* Main layout and spacing */
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Typography and colors */
    :root {
        --primary-color: #0066cc;
        --secondary-color: #4a90e2;
        --accent-color: #00c853;
        --background-color: #f8f9fa;
        --text-color: #2c3e50;
        --heading-color: #1a237e;
    }

    /* Header styling */
    .header-container {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(to right, rgba(255,255,255,0), rgba(0,102,204,0.1), rgba(255,255,255,0));
    }
    
    .main-title {
        color: var(--heading-color);
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        margin: 0.5rem 0 !important;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        color: var(--text-color);
        font-size: 1.1rem !important;
        opacity: 0.8;
        margin-top: 0.5rem !important;
    }
    
    /* Form styling */
    div[data-testid="stForm"] {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #e0e0e0;
    }
    
    /* Button styling */
    div.stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: var(--secondary-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* DataFrame styling */
    div[data-testid="stDataFrame"] {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* Search box styling */
    .search-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #e0e0e0;
    }
    
    /* SQL box styling */
    .sql-box {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 1.25rem;
        border-radius: 8px;
        font-family: 'Monaco', 'Menlo', monospace;
        margin: 1rem 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
        border: 1px solid #2d2d2d;
    }
    
    /* Input field styling */
    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] select,
    div[data-testid="stDateInput"] input {
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stSelectbox"] select:focus,
    div[data-testid="stDateInput"] input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(0,102,204,0.2);
    }
    
    /* Section headers */
    h3 {
        color: var(--heading-color);
        margin: 2rem 0 1rem 0;
        font-weight: 600;
    }
    
    /* Expander styling */
    div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Success/Info message styling */
    div[data-testid="stSuccessMessage"],
    div[data-testid="stInfoMessage"] {
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# App header with icon and title
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">📝 Use Case Tracker</h1>
        <p class="subtitle">Track and manage your use cases efficiently</p>
    </div>
""", unsafe_allow_html=True)

# Section 1: Use Case Tracker Form
# Create three columns for better layout
left_col, center_col, right_col = st.columns([1, 2, 1])

with center_col:
    # Create a form for user input with improved styling
    with st.form("user_form"):
        st.markdown("### Add New Use Case")
        usecase_name = st.text_input("Use Case Name", placeholder="Enter use case name")
        env_needed = st.multiselect(
            "Environment Needed",
            options=["sbx", "dev", "acc", "prd"],
            help="Select one or more environments"
        )
        key_contact = st.text_input("Key Contact", placeholder="Enter key contact")
        L2 = st.text_input("L2", placeholder="Enter L2")
        BL = st.text_input("Business Line", placeholder="Enter business line")
        support_type = st.selectbox(
            "Support Type",
            options=["", "migration", "onboarding"],
            help="Select the type of support needed"
        )
        sub = st.text_input("Subscription", placeholder="Enter subscription Environment")
        ads = st.text_input("ADS", placeholder="Enter Active Directory Groups")
        sps = st.text_input("SPS", placeholder="Enter Service Principal Names")
        data_connections = st.text_area("Data Connections", placeholder="Enter data connections",help="Ex: SnowFlake Data connections")
        started_provision_access_on = st.date_input(
            "Started Provision Access On",
            help="Select the start date"
        )
        support_finished_on = st.date_input(
            "Support Finished On",
            help="Select the end date"
        )
        current_stage = st.selectbox(
            "Current Stage",
            options=["", "Provision Access", "Not Started Yet", "Prod Readiness Testing", "Finished"],
            help="Select the current stage of the use case"
        )
        l2_costcenter = st.text_input("L2 Cost Center", placeholder="Enter L2 cost center")
        note = st.text_area("Notes", placeholder="Enter any additional notes")
        
        # Submit button
        submit_button = st.form_submit_button("➕ Add Use Case")

cfg = Config()  # Set the DATABRICKS_HOST environment variable when running locally

# Permanent variables for connection
HTTP_PATH = "/sql/1.0/warehouses/f3de4cf2e0a0683c"
TABLE_NAME = "dbxappscatalog.demo_schema.demo_usecase_tracker"

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

def insert_data(table_name, conn, usecase_data):
    with conn.cursor() as cursor:
        # Join env_needed list as comma-separated string
        env_needed_str = ','.join(usecase_data['env_needed'])
        query = f"""
        INSERT INTO {table_name} (
            env_needed, usercase_name, key_contact, L2, BL, support_type,
            sub, ads, sps, data_connections, started_provision_access_on,
            support_finished_on, current_stage, l2_costcenter, note
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """
        cursor.execute(query, [
            env_needed_str,
            usecase_data['usecase_name'],
            usecase_data['key_contact'],
            usecase_data['L2'],
            usecase_data['BL'],
            usecase_data['support_type'],
            usecase_data['sub'],
            usecase_data['ads'],
            usecase_data['sps'],
            usecase_data['data_connections'],
            usecase_data['started_provision_access_on'],
            usecase_data['support_finished_on'],
            usecase_data['current_stage'],
            usecase_data['l2_costcenter'],
            usecase_data['note']
        ])
        conn.commit()

def generate_sql_query(natural_query, table_name):
    """Convert natural language query to SQL using Databricks SQL AI Query, optimized for the new table structure."""
    with conn.cursor() as cursor:
        try:
            # Explicitly list columns and describe env_needed as comma-separated string
            table_description = (
                "The table has the following columns: "
                "env_needed (comma-separated environments, e.g. 'sbx,dev,prd'), "
                "usercase_name (use case name), key_contact, L2, BL, support_type, sub, ads, sps, "
                "data_connections, started_provision_access_on (date), support_finished_on (date), "
                "current_stage, l2_costcenter, note. "
                "Return only the SQL query, no explanations."
            )
            prompt = f"You are a SQL expert. {table_description} The table name is {table_name}. Request: {natural_query}"
            query = f"""
            SELECT ai_query(
                'databricks-meta-llama-3-3-70b-instruct',
                ?,
                modelParameters => named_struct('temperature', 0.1, 'max_tokens', 300),
                responseFormat => '{{"type": "text"}}',
                failOnError => false
            ) AS generated_sql
            """
            cursor.execute(query, [prompt])
            result = cursor.fetchone()
            
            # Handle the response
            if result and result[0]:
                response = result[0]
                if isinstance(response, dict):
                    # Extract SQL from result dictionary
                    sql = response.get('result', '')
                else:
                    sql = response

                # Clean up the SQL query
                # Remove markdown code blocks if present
                sql = sql.replace('```sql', '').replace('```', '').strip()
                return sql
            return None
        except Exception as e:
            st.error(f"Error generating SQL query: {str(e)}")
            return None

def execute_generated_query(sql_query):
    """Execute the generated SQL query with safety checks"""
    if not sql_query:
        return None
        
    # Basic SQL injection prevention
    unsafe_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT']
    sql_upper = sql_query.upper() if isinstance(sql_query, str) else ''
    if any(keyword in sql_upper for keyword in unsafe_keywords):
        st.error("Generated query contains unsafe operations. Query rejected.")
        return None
        
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql_query)
            return cursor.fetchall_arrow().to_pandas()
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            return None

# Section 2: Use Case Records
if submit_button and usecase_name and key_contact:  # Minimum required fields
    try:
        conn = get_connection(HTTP_PATH)
        
        # Prepare the data
        usecase_data = {
            'env_needed': env_needed,
            'usecase_name': usecase_name,
            'key_contact': key_contact,
            'L2': L2,
            'BL': BL,
            'support_type': support_type,
            'sub': sub,
            'ads': ads,
            'sps': sps,
            'data_connections': data_connections,
            'started_provision_access_on': started_provision_access_on,
            'support_finished_on': support_finished_on,
            'current_stage': current_stage,
            'l2_costcenter': l2_costcenter,
            'note': note
        }
        
        # Insert the new data
        insert_data(TABLE_NAME, conn, usecase_data)
        
        # Show success message with animation
        st.success("✅ Use Case successfully added!")
        
        # Fetch and display updated data
        df = read_table(TABLE_NAME, conn)
        
        # Display the records
        st.markdown("### 📊 Use Case Records")
        with st.expander("View All Use Cases Info", expanded=False):
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "usecase_name": "Use Case Name",
                    "env_needed": "Environment",
                    "key_contact": "Key Contact",
                    "L2": "L2",
                    "BL": "Business Line",
                    "support_type": "Support Type",
                    "sub": "Subscription",
                    "ads": "ADS",
                    "sps": "SPS",
                    "data_connections": "Data Connections",
                    "started_provision_access_on": "Started On",
                    "support_finished_on": "Finished On",
                    "current_stage": "Current Stage",
                    "l2_costcenter": "L2 Cost Center",
                    "note": "Notes"
            }
        )
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
else:
    conn = get_connection(HTTP_PATH)
    df = read_table(TABLE_NAME, conn)
    
    # Display the records
    st.markdown("### 📊 Use Case Records")
    with st.expander("View All Use Cases", expanded=False):
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "usecase_name": "Use Case Name",
                "env_needed": "Environment",
                "key_contact": "Key Contact",
                "L2": "L2",
                "BL": "Business Line",
                "support_type": "Support Type",
                "sub": "Subscription",
                "ads": "ADS",
                "sps": "SPS",
                "data_connections": "Data Connections",
                "started_provision_access_on": "Started On",
                "support_finished_on": "Finished On",
                "current_stage": "Current Stage",
                "l2_costcenter": "L2 Cost Center",
                "note": "Notes"
        }
    )

# Add AI Search section after Use Case Records
st.markdown("### 🤖 AI-Powered Search")
with st.expander("Ask questions about your data in natural language"):
    st.info("""
    Try asking questions like:
    - List all use cases still in progress
    - What is the average time from started_provision_access_on to support_finished_on by support_type?
    - Find use cases provisioned in the last 30 days
    """)
    
    natural_query = st.text_input(
        "Ask a question about the data (Press Enter ↵)",
        placeholder="Example: List all use cases still in progress",
        key="ai_search"
    )
    
    if natural_query:
        conn = get_connection(HTTP_PATH)
        with st.spinner("Generating SQL query..."):
            generated_sql = generate_sql_query(natural_query, TABLE_NAME)
        
        if generated_sql:
            st.markdown("Generated SQL Query:")
            st.markdown(f"<div class='sql-box'>{generated_sql}</div>", unsafe_allow_html=True)
            
            if st.button("🚀 Run Query"):
                with st.spinner("Executing query..."):
                    results = execute_generated_query(generated_sql)
                if results is not None:
                    if len(results) == 0:
                        st.info("No results found for your query.")
                    else:
                        st.dataframe(
                            results,
                            use_container_width=True,
                            column_config={
                                "usecase_name": "Use Case Name",
                                "env_needed": "Environment",
                                "key_contact": "Key Contact", 
                                "L2": "L2",
                                "BL": "Business Line",
                                "support_type": "Support Type",
                                "sub": "Subscription",
                                "ads": "ADS",
                                "sps": "SPS",
                                "data_connections": "Data Connections",
                                "started_provision_access_on": "Started On",
                                "support_finished_on": "Finished On",
                                "current_stage": "Current Stage",
                                "l2_costcenter": "L2 Cost Center",
                                "note": "Notes"
                            }
                        )
