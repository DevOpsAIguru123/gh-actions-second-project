Create a New Delta Table
This query creates a new table named AggregatedProjectCosts with your summarized data. The table will be created in the Parquet-based Delta Lake format.
#######################################################
CREATE OR REPLACE TABLE AggregatedProjectCosts
USING delta
AS
SELECT
  Month,
  Project,
  SUM(PretaxCost) AS MonthlyProjectCost
FROM
  (
    SELECT
      PretaxCost,
      date_format(UsageDateTime, 'yyyy-MM') AS Month,
      COALESCE(
        -- 1. First, check the 'project' tag
        CASE get_json_object(Tags, '$.project')
            WHEN 'demo11' THEN 'demo11'
            WHEN 'demo12' THEN 'demo11' -- Rename
            WHEN 'test11' THEN 'test11'
            WHEN 'test12' THEN 'test11' -- Rename
        END,
        -- 2. Fall back to the 'creator' tag
        CASE get_json_object(Tags, '$.creator')
            WHEN 'y111' THEN 'demo11'
            WHEN 'x111' THEN 'test11'
        END
      ) AS Project
    FROM
      YourTable -- Replace 'YourTable' with the name of your source table
  ) AS ProjectData
WHERE
  Project IS NOT NULL
GROUP BY
  Month,
  Project;


######################

Append or Overwrite an Existing Table
If you plan to run this aggregation periodically, you might want to overwrite the table's contents instead of dropping and recreating it. For that, you would use INSERT OVERWRITE.

First, you would create the table structure one time


CREATE TABLE AggregatedProjectCosts (
  Month STRING,
  Project STRING,
  MonthlyProjectCost DOUBLE
) USING delta;


Then, you can run this query on a schedule to refresh the data:


INSERT OVERWRITE AggregatedProjectCosts
SELECT
  -- The rest of the query is the same as above
  Month,
  Project,
  SUM(PretaxCost) AS MonthlyProjectCost
FROM
  (
    SELECT
      PretaxCost,
      date_format(UsageDateTime, 'yyyy-MM') AS Month,
      COALESCE(
        -- ... logic from above
      ) AS Project
    FROM
      YourTable
  ) AS ProjectData
WHERE
  Project IS NOT NULL
GROUP BY
  Month,
  Project;

########## gpt #########
  from pyspark.sql import functions as F
from pyspark.sql.types import MapType, StringType

# Load the raw cost export
df = spark.table("billingdata")

# Parse the Tags JSON string into a map of key/value pairs.
# Tags are stored as a JSON object per row:contentReference[oaicite:0]{index=0}, so from_json()
# turns them into a MapType column for easy access.
df = df.withColumn(
    "tags_map",
    F.from_json("Tags", MapType(StringType(), StringType()))
)

# Extract the project and creator tags
df = df.withColumn("project_tag", df.tags_map["project"]) \
       .withColumn("creator_tag", df.tags_map["creator"])

# Define a normalised project value
df = df.withColumn(
    "project_normalised",
    F.when(df.project_tag.isin("demo11", "demo12"), "demo11")
     .when(df.project_tag.isin("test11", "test12"), "test11")
     .when(df.project_tag.isNull() & (df.creator_tag == "y111"), "demo11")
     .when(df.project_tag.isNull() & (df.creator_tag == "x111"), "test11")
     .otherwise(df.project_tag)
)

# Derive the first day of the month from the usage date/time
df = df.withColumn("month_start", F.trunc("UsageDateTime", "MM"))

# Aggregate costs by month and normalised project name.
# Replace 'EffectiveCost' with the appropriate cost column (e.g., 'BilledCost')
agg_df = (df.groupBy("month_start", "project_normalised")
             .agg(F.sum("EffectiveCost").alias("total_cost"))
          )

# Persist as a Delta table; overwrite to refresh data each run.
agg_df.write.format("delta").mode("overwrite").saveAsTable("costproject")
