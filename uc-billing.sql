CREATE TABLE IF NOT EXISTS monthly_workspace_summary (
  year_month STRING,
  workspace_id STRING,
  workspace_name STRING,
  total_cost DECIMAL(19,4),
  products_used INT,
  skus_used INT,
  last_updated TIMESTAMP
) USING DELTA;

-- Insert/Update monthly summaries
MERGE INTO monthly_workspace_summary t
USING (
  SELECT
    DATE_FORMAT(u.usage_date, 'yyyy-MM') AS year_month,
    u.workspace_id,
    COALESCE(w.workspace_name, 'Workspace_' || u.workspace_id) AS workspace_name,
    SUM(u.usage_quantity * COALESCE(p.list_price, 0)) AS total_cost,
    COUNT(DISTINCT u.billing_origin_product) AS products_used,
    COUNT(DISTINCT u.sku_name) AS skus_used,
    CURRENT_TIMESTAMP() AS last_updated
  FROM system.billing.usage u
  LEFT JOIN system.access.workspaces_latest w
    ON u.workspace_id = w.workspace_id
  LEFT JOIN system.billing.list_prices p
    ON u.sku_name = p.sku_name
    AND u.cloud = p.cloud
    AND u.usage_start_time >= p.price_start_time
    AND (u.usage_start_time < p.price_end_time OR p.price_end_time IS NULL)
  WHERE u.workspace_id IN ('123456', '123457')
    AND u.usage_quantity != 0
  GROUP BY 
    DATE_FORMAT(u.usage_date, 'yyyy-MM'),
    u.workspace_id,
    w.workspace_name
) s
ON t.year_month = s.year_month AND t.workspace_id = s.workspace_id
WHEN MATCHED THEN UPDATE SET 
  t.workspace_name = s.workspace_name,
  t.total_cost = s.total_cost,
  t.products_used = s.products_used,
  t.skus_used = s.skus_used,
  t.last_updated = s.last_updated
WHEN NOT MATCHED THEN INSERT 
  (year_month, workspace_id, workspace_name, total_cost, products_used, skus_used, last_updated)
VALUES 
  (s.year_month, s.workspace_id, s.workspace_name, s.total_cost, s.products_used, s.skus_used, s.last_updated);
