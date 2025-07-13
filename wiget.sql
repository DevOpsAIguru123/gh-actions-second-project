– Time period options (for dropdown population) - Keep this dataset as is
SELECT
*
FROM
VALUES
(‘Last Month’),
(‘Last 3 Months’),
(‘Last 6 Months’),
(‘Last 12 Months’)
AS time_periods(period_name);

– Main query with dynamic time filtering (REMOVE the parameter)
SELECT *
FROM entai_development_catalog.vinod_databricks_dashboard.monthly_active_users_by_workspace
WHERE
to_date(concat(‘year-month’, ‘-01’)) >=
CASE
– This will be controlled by the dropdown filter widget instead of parameter
WHEN ‘Last Month’ IN (SELECT period_name FROM time_periods) THEN date_trunc(‘month’, add_months(current_date(), -1))
WHEN ‘Last 3 Months’ IN (SELECT period_name FROM time_periods) THEN date_trunc(‘month’, add_months(current_date(), -3))
WHEN ‘Last 6 Months’ IN (SELECT period_name FROM time_periods) THEN date_trunc(‘month’, add_months(current_date(), -6))
WHEN ‘Last 12 Months’ IN (SELECT period_name FROM time_periods) THEN date_trunc(‘month’, add_months(current_date(), -12))
ELSE date_trunc(‘month’, add_months(current_date(), -3)) – Default to 3 months
END
AND to_date(concat(‘year-month’, ‘-01’)) < date_trunc(‘month’, current_date())
ORDER BY
‘year-month’ ASC;