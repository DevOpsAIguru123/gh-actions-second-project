– Main query that uses the static parameter
SELECT *
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
ELSE date_trunc(‘month’, add_months(current_date(), -3)) – Default to 3 months
END
ORDER BY month_column DESC