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

---- tag missing
WITH prices AS (
  SELECT
    *,
    coalesce(price_end_time, date_add(current_date, 1)) as coalesced_price_end_time
  FROM
    system.billing.list_prices
  WHERE
    currency_code = 'USD'
),
-- This CTE calculates the cost and creates a new, corrected project tag column
usage_with_corrected_tags AS (
  SELECT
    u.usage_date,
    u.workspace_id,
    coalesce(u.usage_quantity * p.pricing.effective_list.default, 0) AS list_price_usd,
    -- ############### EDIT THIS SECTION ###############
    -- Add a WHEN block for each service principal whose costs you need to re-assign.
    CASE
      -- Scenario 1: A specific job owner is found and the 'project' tag is missing.
      WHEN u.identity_metadata.run_as = 'service-principal-A@your-domain.com' AND u.custom_tags['project'] IS NULL
        THEN 'Project_Alpha'

      -- Scenario 2: Add another service principal and project.
      WHEN u.identity_metadata.run_as = 'service-principal-B@your-domain.com' AND u.custom_tags['project'] IS NULL
        THEN 'Project_Beta'
        
      -- For all other records, use the 'project' tag if it exists.
      ELSE u.custom_tags['project']
    END AS project_tag
    -- ###############################################
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
    -- Optional: You can filter for specific workspaces if needed
    u.workspace_id IN ('118465356851554', '3471645455711595')
)
-- Final aggregation by the new, corrected project tag
SELECT
  DATE_TRUNC('MONTH', usage_date) AS usage_month,
  project_tag,
  SUM(list_price_usd) AS total_list_price_usd
FROM
  usage_with_corrected_tags
WHERE
  project_tag IS NOT NULL -- Exclude records that never had a project tag
GROUP BY
  usage_month,
  project_tag
ORDER BY
  usage_month DESC,
  total_list_price_usd DESC;

