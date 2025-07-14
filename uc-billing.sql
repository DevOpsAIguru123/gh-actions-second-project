------ workspace by monthly
%sql
---- Plan C
WITH prices AS (
  SELECT
    *,
    coalesce(price_end_time, date_add(current_date, 1)) as coalesced_price_end_time
  FROM
    system.billing.list_prices
  WHERE
    currency_code = 'USD'
)
SELECT
  CASE u.workspace_id
    WHEN '118465356851554' THEN 'dbx-dev'
    WHEN '3471645455711595' THEN 'dbx-text'
  END AS workspace_name,
  u.workspace_id,
  DATE_TRUNC('MONTH', u.usage_date) AS usage_month,
  SUM(coalesce(u.usage_quantity * p.pricing.effective_list.default, 0)) AS total_list_price_usd
FROM
  system.billing.usage AS u
LEFT JOIN
  prices AS p
  ON u.sku_name = p.sku_name
  AND u.usage_unit = p.usage_unit
  AND (
    u.usage_end_time BETWEEN p.price_start_time
    AND p.coalesced_price_end_time
  )
WHERE
  u.workspace_id IN ('118465356851554', '3471645455711595')
GROUP BY
  workspace_name,
  u.workspace_id,
  usage_month
ORDER BY
  usage_month ASC,
  workspace_name;

------ Workspace usage by sku 
WITH prices AS (
  SELECT
    *,
    coalesce(price_end_time, date_add(current_date, 1)) as coalesced_price_end_time
  FROM
    system.billing.list_prices
  WHERE
    currency_code = 'USD'
)
SELECT
  CASE u.workspace_id
    WHEN '118465356851554' THEN 'dbx-dev'
    WHEN '3471645455711595' THEN 'dbx-text'
  END AS workspace_name,
  u.workspace_id,
  DATE_TRUNC('MONTH', u.usage_date) AS usage_month,
  u.sku_name,
  SUM(coalesce(u.usage_quantity * p.pricing.effective_list.default, 0)) AS total_list_price_usd
FROM
  system.billing.usage AS u
LEFT JOIN
  prices AS p
  ON u.sku_name = p.sku_name
  AND u.usage_unit = p.usage_unit
  AND (
    u.usage_end_time BETWEEN p.price_start_time
    AND p.coalesced_price_end_time
  )
WHERE
  u.workspace_id IN ('118465356851554', '3471645455711595')
GROUP BY
  workspace_name,
  u.workspace_id,
  usage_month,
  u.sku_name
ORDER BY
  usage_month ASC,
  workspace_name,
  total_list_price_usd DESC;


---- Workspace usage by product
WITH prices AS (
  SELECT
    *,
    coalesce(price_end_time, date_add(current_date, 1)) as coalesced_price_end_time
  FROM
    system.billing.list_prices
  WHERE
    currency_code = 'USD'
)
SELECT
  CASE u.workspace_id
    WHEN '118465356851554' THEN 'dbx-dev'
    WHEN '3471645455711595' THEN 'dbx-text'
  END AS workspace_name,
  u.workspace_id,
  DATE_TRUNC('MONTH', u.usage_date) AS usage_month,
  u.billing_origin_product,
  SUM(coalesce(u.usage_quantity * p.pricing.effective_list.default, 0)) AS total_list_price_usd
FROM
  system.billing.usage AS u
LEFT JOIN
  prices AS p
  ON u.sku_name = p.sku_name
  AND u.usage_unit = p.usage_unit
  AND (
    u.usage_end_time BETWEEN p.price_start_time
    AND p.coalesced_price_end_time
  )
WHERE
  u.workspace_id IN ('118465356851554', '3471645455711595')
GROUP BY
  workspace_name,
  u.workspace_id,
  usage_month,
  u.billing_origin_product
ORDER BY
  usage_month ASC,
  workspace_name,
  total_list_price_usd DESC;

---- update tags
WITH prices AS (
  SELECT
    *,
    coalesce(price_end_time, date_add(current_date, 1)) as coalesced_price_end_time
  FROM
    system.billing.list_prices
  WHERE
    currency_code = 'USD'
)
SELECT
  DATE_TRUNC('MONTH', u.usage_date) AS usage_month,
  CASE u.workspace_id
    WHEN '118465356851554' THEN 'dbx-dev'
    WHEN '3471645455711595' THEN 'dbx-text'
  END AS workspace_name,
  u.workspace_id,
  t.tag_key,
  t.tag_value,
  SUM(coalesce(u.usage_quantity * p.pricing.effective_list.default, 0)) AS total_list_price_usd
FROM
  system.billing.usage AS u,
  LATERAL explode(u.custom_tags) AS t(tag_key, tag_value)
LEFT JOIN
  prices AS p
  ON u.sku_name = p.sku_name
  AND u.usage_unit = p.usage_unit
  AND (
    u.usage_end_time BETWEEN p.price_start_time
    AND p.coalesced_price_end_time
  )
WHERE
  u.workspace_id IN ('118465356851554', '3471645455711595')
GROUP BY
  usage_month,
  workspace_name,
  u.workspace_id,
  t.tag_key,
  t.tag_value
ORDER BY
  usage_month DESC,
  total_list_price_usd DESC;

