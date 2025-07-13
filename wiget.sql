– Dataset 1: Static parameter options (for filter widget)
SELECT * FROM (
VALUES
(‘Last Month’),
(‘Last 3 Months’),
(‘Last 6 Months’),
(‘Last 12 Months’)
) AS time_periods(period_name)

– Dataset 2: Main data query with parameter
SELECT
month_column,
revenue,
orders,
customers,
– Add other aggregated metrics
FROM your_monthly_aggregated_table
WHERE month_column >=
CASE
WHEN :time_period_param = ‘Last Month’ THEN
date_trunc(‘month’, add_months(current_date(), -1))
WHEN :time_period_param = ‘Last 3 Months’ THEN
date_trunc(‘month’, add_months(current_date(), -3))
WHEN :time_period_param = ‘Last 6 Months’ THEN
date_trunc(‘month’, add_months(current_date(), -6))
WHEN :time_period_param = ‘Last 12 Months’ THEN
date_trunc(‘month’, add_months(current_date(), -12))
ELSE date_trunc(‘month’, add_months(current_date(), -3))
END
ORDER BY month_column DESC

– Alternative: If your month_column is stored as string (YYYY-MM format)
SELECT
month_column,
revenue,
orders,
customers
FROM your_monthly_aggregated_table
WHERE month_column >=
CASE
WHEN :time_period_param = ‘Last Month’ THEN
date_format(add_months(current_date(), -1), ‘yyyy-MM’)
WHEN :time_period_param = ‘Last 3 Months’ THEN
date_format(add_months(current_date(), -3), ‘yyyy-MM’)
WHEN :time_period_param = ‘Last 6 Months’ THEN
date_format(add_months(current_date(), -6), ‘yyyy-MM’)
WHEN :time_period_param = ‘Last 12 Months’ THEN
date_format(add_months(current_date(), -12), ‘yyyy-MM’)
ELSE date_format(add_months(current_date(), -3), ‘yyyy-MM’)
END
ORDER BY month_column DESC