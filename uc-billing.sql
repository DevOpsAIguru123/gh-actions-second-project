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

# Define the main MERGE statement to upsert all historical data for the specified workspaces.
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
      SUM(u.usage_quantity * p.pricing.default) AS estimated_cost_usd
    FROM
      system.billing.usage AS u
    JOIN
      system.billing.list_prices AS p
        ON u.sku_name = p.sku_name
        AND u.usage_start_time >= p.price_start_time
        AND (u.usage_start_time < p.price_end_time OR p.price_end_time IS NULL)
    LEFT JOIN
      system.access.workspaces_latest AS ws
        ON u.workspace_id = ws.workspace_id
    WHERE
      u.workspace_id IN (12323444, 343434554) -- Filters for your specific workspaces
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

# Execute the SQL commands using spark.sql()
spark.sql(create_table_sql)
spark.sql(merge_sql)

print("Historical billing aggregation complete for the specified workspaces.")
