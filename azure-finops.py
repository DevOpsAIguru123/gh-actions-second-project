# This is for your ONE-TIME historical load
# This is for your ONE-TIME historical load
# CORRECTED to use the 'ChargePeriodStart' column.

from pyspark.sql.functions import col, date_format

# The date column from the FOCUS schema that represents the date of the charge.
# This is the correct column to use for monthly partitioning.
date_column_for_partitioning = "ChargePeriodStart" 

# Define paths and table name
source_path = ""
delta_table_name = ""

print(f"Reading historical data from: {source_path}")

# Read the source data
df = spark.read.parquet(source_path)

# Add a 'year_month' column for partitioning (e.g., '2025-07')
# This is created by formatting the 'ChargePeriodStart' date.
df_with_partition = df.withColumn("year_month", date_format(col(date_column_for_partitioning), "yyyy-MM"))

print(f"Writing partitioned data to Delta table: {delta_table_name}")

# Write to Delta table, partitioned by the new 'year_month' column
df_with_partition.write \
  .format("delta") \
  .partitionBy("year_month") \
  .mode("overwrite") \
  .saveAsTable(delta_table_name)

print(f"✅ Successfully created and partitioned Delta table: {delta_table_name}")


###################################################################
# ============== INCREMENTAL INGESTION NOTEBOOK (FINAL) ==============
# Schedule this notebook to run weekly or daily.
# No changes were needed for this script. It works correctly with the partitioned table.

import datetime
from pyspark.sql.functions import col, lit

# --- 1. Define Configuration ---
# Get the current month as a string 'YYYY-MM' (e.g., '2025-07')
current_month_str = datetime.date.today().strftime("%Y-%m")
# Get the current month's date range start 'YYYYMM' (e.g., '202507') for finding the folder
current_month_folder_prefix = datetime.date.today().strftime("%Y%m")

# Define paths
# Using a wildcard (*) to find the folder for the current month (e.g., 20250701-20250731)
source_path_current_month = f"/Volumes/entai_sandbox_catalog/eai_usage_v1/azurefinops/volume/azurefinops/azurefinops-focus-cost/*/{current_month_folder_prefix}*/*.parquet"
delta_table_name = "entai_sandbox_catalog.eai_usage_v1.azure_billing_data"

print(f"Processing month: {current_month_str}")
print(f"Reading from source: {source_path_current_month}")

# --- 2. Read the Current Month's Data from Source ---
try:
  df_current = spark.read.parquet(source_path_current_month)
except Exception as e:
  # This handles cases where the folder might not exist yet at the very beginning of a month.
  print(f"No data found for current month '{current_month_str}'. Skipping run. Error: {e}")
  dbutils.notebook.exit("No data for current month") # Exit the notebook gracefully

# Check if the dataframe is empty
if df_current.rdd.isEmpty():
    print(f"Source directory for month {current_month_str} is empty. Skipping run.")
    dbutils.notebook.exit("Source is empty")

# --- 3. Prepare DataFrame for Writing ---
# IMPORTANT: Explicitly add the 'year_month' column to the DataFrame.
# This ensures the data being written has the partition column needed for `replaceWhere`.
df_to_write = df_current.withColumn("year_month", lit(current_month_str))


# --- 4. Write to Delta Table using replaceWhere ---
# This atomically deletes all data matching the condition and inserts the new data.
# This is the best practice for handling cumulative snapshots.

print(f"Writing {df_to_write.count()} rows to the '{current_month_str}' partition...")

df_to_write.write \
  .format("delta") \
  .mode("overwrite") \
  .option("replaceWhere", f"year_month = '{current_month_str}'") \
  .saveAsTable(delta_table_name)

print(f"✅ Successfully updated month {current_month_str} in Delta table {delta_table_name}.")



############### month to date problem ###
# ============== INCREMENTAL INGESTION NOTEBOOK (WITH MONTH-END CATCH-UP) ==============
# This robust version processes BOTH the current and previous months on each run.
# This ensures that the final, complete data for the previous month is captured
# during the first week of a new month.

import datetime
from dateutil.relativedelta import relativedelta
from pyspark.sql.functions import col, lit

# --- 1. Reusable Function to Process a Specific Month ---
def process_month(month_date):
    """
    Reads all parquet files for a given month, and replaces the corresponding
    partition in the target Delta table.
    
    Args:
        month_date (datetime.date): A date object representing the month to process.
    """
    month_str = month_date.strftime("%Y-%m")
    month_folder_prefix = month_date.strftime("%Y%m")
    
    source_path = f" "
    delta_table_name = " "

    print(f"--- Processing month: {month_str} ---")
    print(f"Reading from source: {source_path}")

    try:
        df_month = spark.read.parquet(source_path)
    except Exception as e:
        # It's normal for a folder not to exist (e.g., no data for the previous month on the very first run).
        print(f"No data found for month '{month_str}'. Skipping. Error: {e}")
        return # Exit the function for this month

    if df_month.rdd.isEmpty():
        print(f"Source directory for month {month_str} is empty. Skipping.")
        return

    # Prepare DataFrame by adding the partition column
    df_to_write = df_month.withColumn("year_month", lit(month_str))

    # Atomically replace the data for this specific month's partition
    print(f"Writing {df_to_write.count()} rows to the '{month_str}' partition...")
    df_to_write.write \
      .format("delta") \
      .mode("overwrite") \
      .option("replaceWhere", f"year_month = '{month_str}'") \
      .saveAsTable(delta_table_name)
      
    print(f"✅ Successfully updated partition '{month_str}'.")


# --- 2. Main Script Logic ---
# Get today's date
today = datetime.date.today()

# Define current and previous months
current_month_date = today
previous_month_date = today - relativedelta(months=1)

# Process the previous month to catch any final updates
process_month(previous_month_date)

# Process the current month for the latest month-to-date data
process_month(current_month_date)

print("\n--- Incremental load finished. ---")




########### Latest #############
# ============== INCREMENTAL INGESTION NOTEBOOK (WITH MONTH-END CATCH-UP) ==============
# This robust version processes BOTH the current and previous months on each run.
# This ensures that the final, complete data for the previous month is captured
# during the first week of a new month.

import datetime
from dateutil.relativedelta import relativedelta
from pyspark.sql.functions import col, lit

# --- 1. Reusable Function to Process a Specific Month ---
def process_month(month_date):
    """
    Reads all parquet files for a given month, and replaces the corresponding
    partition in the target Delta table.
    
    Args:
        month_date (datetime.date): A date object representing the month to process.
    """
    month_str = month_date.strftime("%Y-%m")
    month_folder_prefix = month_date.strftime("%Y%m")
    
    source_path = f"/Volumes/entai_sandbox_catalog/eai_usage_v1/azurefinops/volume/azurefinops/azurefinops-focus-cost/*/{month_folder_prefix}*/*.parquet"
    delta_table_name = "entai_sandbox_catalog.eai_usage_v1.azure_billing_data"

    print(f"--- Processing month: {month_str} ---")
    print(f"Reading from source: {source_path}")

    try:
        df_month = spark.read.parquet(source_path)
    except Exception as e:
        # It's normal for a folder not to exist (e.g., no data for the previous month on the very first run).
        print(f"No data found for month '{month_str}'. Skipping. Error: {e}")
        return # Exit the function for this month

    if df_month.rdd.isEmpty():
        print(f"Source directory for month {month_str} is empty. Skipping.")
        return

    # Prepare DataFrame by adding the partition column
    df_to_write = df_month.withColumn("year_month", lit(month_str))

    # Atomically replace the data for this specific month's partition
    print(f"Writing {df_to_write.count()} rows to the '{month_str}' partition...")
    df_to_write.write \
      .format("delta") \
      .mode("overwrite") \
      .option("replaceWhere", f"year_month = '{month_str}'") \
      .saveAsTable(delta_table_name)
      
    print(f"✅ Successfully updated partition '{month_str}'.")


# --- 2. Main Script Logic ---
# Get today's date
today = datetime.date.today()

# Define current and previous months
current_month_date = today
previous_month_date = today - relativedelta(months=1)

# Process the previous month to catch any final updates
process_month(previous_month_date)

# Process the current month for the latest month-to-date data
process_month(current_month_date)

print("\n--- Incremental load finished. ---")

