# Define the SQL statement to create the target table if it doesn't exist.
create_table_sql = """
  CREATE TABLE IF NOT EXISTS your_catalog.your_schema.monthly_billing_summary (
    year_month STRING,
    workspace_id BIGINT,
    workspace_name STRING,
    billing_origin_product STRING,
    sku_name STRING,
    usage_unit STRING,
    total_usage_quantity DECIMAL(18, 3),
    estimated_cost_usd DECIMAL(18, 2)
  )
"""

# Define the main MERGE statement to upsert the monthly aggregated data.
merge_sql = """
  MERGE INTO your_catalog.your_schema.monthly_billing_summary AS target
  USING (
    SELECT
      date_format(u.usage_start_time, 'yyyy-MM') AS year_month,
      u.workspace_id,
      ws.workspace_name,
      u.billing_origin_product,
      u.sku_name,
      u.usage_unit,
      SUM(u.usage_quantity) as total_usage_quantity,
      SUM(u.usage_quantity * p.price_per_unit) AS estimated_cost_usd
    FROM
      system.billing.usage AS u
    JOIN
      system.billing.list_prices AS p
        ON u.sku_name = p.sku_name
        AND u.usage_start_time >= p.price_start_time
        AND (u.usage_start_time < p.price_end_time OR p.price_end_time IS NULL)
    LEFT JOIN
      system.account.workspaces AS ws
        ON u.workspace_id = ws.workspace_id
    WHERE
      u.usage_start_time >= date_trunc('month', add_months(current_date(), -1))
      AND u.usage_start_time < date_trunc('month', current_date())
    GROUP BY
      1, 2, 3, 4, 5, 6
  ) AS source
  ON
    target.year_month = source.year_month
    AND target.workspace_id = source.workspace_id
    AND target.billing_origin_product = source.billing_origin_product
    AND target.sku_name = source.sku_name
  WHEN MATCHED THEN
    UPDATE SET
      total_usage_quantity = source.total_usage_quantity,
      estimated_cost_usd = source.estimated_cost_usd
  WHEN NOT MATCHED THEN
    INSERT (
      year_month,
      workspace_id,
      workspace_name,
      billing_origin_product,
      sku_name,
      usage_unit,
      total_usage_quantity,
      estimated_cost_usd
    )
    VALUES (
      source.year_month,
      source.workspace_id,
      source.workspace_name,
      source.billing_origin_product,
      source.sku_name,
      source.usage_unit,
      source.total_usage_quantity,
      source.estimated_cost_usd
    )
"""

# 1. Execute the CREATE TABLE statement
spark.sql(create_table_sql)

# 2. Execute the MERGE statement
spark.sql(merge_sql)

print("Billing aggregation complete and data has been merged into the summary table.")
