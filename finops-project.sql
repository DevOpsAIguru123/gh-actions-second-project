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
