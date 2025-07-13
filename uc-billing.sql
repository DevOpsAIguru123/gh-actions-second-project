-- Step 1: Ensure the destination table exists with the new column
CREATE TABLE IF NOT EXISTS ucdbx.billing.monthly_billing_summary (
  year_month STRING,
  workspace_id BIGINT,
  workspace_name STRING,
  billing_origin_product STRING, -- Added column
  sku_name STRING,
  usage_unit STRING,
  total_usage_quantity DECIMAL(18, 3),
  estimated_cost_usd DECIMAL(18, 2)
);

-- Step 2: Merge the latest monthly data into your permanent table
MERGE INTO ucdbx.billing.monthly_billing_summary AS target
USING (
  -- Subquery to calculate cost before aggregation
  SELECT
    date_format(u.usage_start_time, 'yyyy-MM') AS year_month,
    u.workspace_id,
    ws.workspace_name,
    u.billing_origin_product, -- Added column
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
    system.access.workspaces_latest AS ws
      ON u.workspace_id = ws.workspace_id
  WHERE
    u.usage_start_time >= date_trunc('month', add_months(current_date(), -1))
    AND u.usage_start_time < date_trunc('month', current_date())
  GROUP BY
    1, 2, 3, 4, 5, 6 -- Added the new column to the grouping
) AS source
ON
  target.year_month = source.year_month
  AND target.workspace_id = source.workspace_id
  AND target.billing_origin_product = source.billing_origin_product -- Added to the join condition
  AND target.sku_name = source.sku_name

-- If a record for that month/workspace/product/SKU already exists, update it
WHEN MATCHED THEN
  UPDATE SET
    total_usage_quantity = source.total_usage_quantity,
    estimated_cost_usd = source.estimated_cost_usd

-- If it's new, insert it
WHEN NOT MATCHED THEN
  INSERT (
    year_month,
    workspace_id,
    workspace_name,
    billing_origin_product, -- Added to the insert list
    sku_name,
    usage_unit,
    total_usage_quantity,
    estimated_cost_usd
  )
  VALUES (
    source.year_month,
    source.workspace_id,
    source.workspace_name,
    source.billing_origin_product, -- Added to the values list
    source.sku_name,
    source.usage_unit,
    source.total_usage_quantity,
    source.estimated_cost_usd
  );
