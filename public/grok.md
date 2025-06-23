To effectively monitor and present Databricks platform usage and billing to stakeholders, you can create dashboards using Databricks' built-in dashboarding capabilities, leveraging system tables like `system.billing.usage` and `system.billing.list_prices`. These dashboards can provide insights into costs, resource usage, and trends, helping stakeholders make informed decisions. Below are key points and detailed recommendations for creating impactful dashboards.

- **Key Dashboards**: Create dashboards for billing overview, usage trends, object usage, resource utilization, and anomaly detection.
- **Data Sources**: Use `system.billing.usage` for cost and usage data, and `system.billing.list_prices` for pricing trends.
- **Customization**: Start with Databricks’ pre-built usage dashboards and customize them for specific needs, such as team-based cost allocation.
- **Tagging**: Implement resource tagging for accurate cost attribution across teams or projects.
- **Interactivity**: Ensure dashboards allow filtering by time, tags, or workspaces for stakeholder flexibility.

### Getting Started with Pre-Built Dashboards
Databricks offers pre-built usage dashboards that you can import and customize for Unity Catalog-enabled workspaces. These dashboards display usage by product, SKU, and custom tags, and are a great starting point. To import them, navigate to the **Usage** tab in the [account console](https://accounts.cloud.databricks.com), select **Setup dashboard**, choose account or workspace-level data, and import. These dashboards use `system.billing.usage` and `system.billing.list_prices` tables, which are free to query and have a 365-day retention period for usage data.

### Suggested Dashboards
Here are five recommended dashboards to effectively showcase usage and billing:

1. **Billing Overview**: Displays total spend, cost by service, and top cost drivers. Use line charts for spend over time and pie charts for SKU breakdowns.
2. **Usage Trends**: Tracks usage (e.g., DBUs, compute hours) over time, by team, or by workspace. Line charts are ideal for showing growth or seasonal patterns.
3. **Object Usage**: Highlights usage and costs for specific objects like notebooks or clusters, using data from `usage_metadata` in `system.billing.usage`.
4. **Resource Utilization**: Monitors cluster and storage efficiency, identifying idle resources or optimization opportunities.
5. **Anomaly Detection**: Flags unexpected spikes in usage or costs, helping stakeholders address issues quickly.

### Customization and Best Practices
To make dashboards impactful, ensure resources are tagged (e.g., by team or project) for cost allocation, and use interactive features like time range filters. For detailed insights, write SQL queries to extract specific metrics, such as costs by notebook or cluster. Regularly update dashboards and refer to Databricks documentation for Azure ([System Tables](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/)) or AWS ([System Tables](https://docs.databricks.com/aws/en/admin/system-tables/)) for guidance.


# Sample SQL Queries for Databricks Usage and Billing Dashboards

Below are example SQL queries to extract key metrics from Databricks system tables for creating usage and billing dashboards. These queries use the `system.billing.usage` and `system.billing.list_prices` tables to provide insights into costs, usage, and object-specific metrics.

## Total Spend by Month
```sql
SELECT 
    DATE_TRUNC('month', usage_date) AS month,
    SUM(usage_amount * pricing.default) AS total_cost
FROM system.billing.usage
JOIN system.billing.list_prices 
    ON system.billing.usage.sku_name = system.billing.list_prices.sku_name
    AND system.billing.usage.usage_date >= system.billing.list_prices.price_start_time
GROUP BY month
ORDER BY month DESC;
```

## Cost by Service/SKU
```sql
SELECT 
    sku_name,
    SUM(usage_amount * pricing.default) AS total_cost
FROM system.billing.usage
JOIN system.billing.list_prices 
    ON system.billing.usage.sku_name = system.billing.list_prices.sku_name
WHERE usage_date >= DATEADD(month, -3, CURRENT_DATE)
GROUP BY sku_name
ORDER BY total_cost DESC
LIMIT 10;
```

## Usage by Notebook
```sql
SELECT 
    usage_metadata.notebook_path,
    SUM(usage_amount) AS total_usage
FROM system.billing.usage
WHERE usage_metadata.notebook_path IS NOT NULL
GROUP BY usage_metadata.notebook_path
ORDER BY total_usage DESC
LIMIT 10;
```

## Cost by Cluster
```sql
SELECT 
    usage_metadata.cluster_name,
    SUM(usage_amount * pricing.default) AS total_cost
FROM system.billing.usage
JOIN system.billing.list_prices 
    ON system.billing.usage.sku_name = system.billing.list_prices.sku_name
WHERE usage_metadata.cluster_name IS NOT NULL
GROUP BY usage_metadata.cluster_name
ORDER BY total_cost DESC
LIMIT 10;
```

## Usage by Team (Using Tags)
```sql
SELECT 
    custom_tags.team,
    SUM(usage_amount * pricing.default) AS total_cost
FROM system.billing.usage
JOIN system.billing.list_prices 
    ON system.billing.usage.sku_name = system.billing.list_prices.sku_name
WHERE custom_tags.team IS NOT NULL
GROUP BY custom_tags.team
ORDER BY total_cost DESC;
```

## Notes
- Ensure you have `ទSELECT permissions on `system.billing.usage` and `system.billing.list_prices`.
- Replace `team` with the appropriate tag name used in your organization.
- Adjust `DATEADD` parameters to change FacetGrid or similar filters for specific time ranges or objects.


---

To create effective Databricks platform usage and billing dashboards for stakeholders, leveraging system tables such as `system.billing.usage` and `system.billing.list_prices`, you can design a comprehensive set of dashboards that provide clear, actionable insights into costs, resource usage, and trends. Below is a detailed guide to creating these dashboards, including key metrics, data sources, and best practices.

### Key Points
- **Key Dashboards**: It seems likely that you can create dashboards for billing overview, usage trends, object usage, resource utilization, and anomaly detection to effectively monitor Databricks platform usage and billing.
- **Data Sources**: The `system.billing.usage` table provides detailed usage and cost data, while `system.billing.list_prices` tracks pricing changes. Additional tables like `system.compute.clusters` and `system.access.audit` offer compute and user activity insights.
- **Customization**: Databricks provides pre-built usage dashboards that can be imported and customized, offering a strong starting point for monitoring usage by product, SKU, and tags.
- **Tagging**: Implementing resource tagging (e.g., by team or project) is recommended for accurate cost allocation across organizational units.
- **Interactivity**: Dashboards should include interactive features like time range filters, tag-based filtering, and drill-down capabilities to enhance stakeholder engagement.

### Getting Started with Pre-Built Dashboards
Databricks offers pre-built usage dashboards for Unity Catalog-enabled workspaces, which can be imported via the [account console](https://accounts.cloud.databricks.com). These dashboards, based on `system.billing.usage` and `system.billing.list_prices`, display usage by product, SKU, and custom tags, and are customizable. To import, go to the **Usage** tab, select **Setup dashboard**, choose account or workspace-level data, select a workspace, and click **Import**. These dashboards are free to use, with usage data retained for 365 days and pricing data stored indefinitely.

### Recommended Dashboards
The following dashboards are recommended to provide stakeholders with comprehensive insights into Databricks usage and billing:

1. **Billing Overview Dashboard**
   - **Purpose**: Provide a high-level view of costs and cost distribution.
   - **Metrics**:
     - Total spend over time (line chart).
     - Spend by service/SKU (bar or pie chart).
     - Top 10 cost drivers (table or bar chart).
     - Budget vs. actual spend (if budget data is available).
   - **Data Source**: `system.billing.usage` for usage and cost data; `system.billing.list_prices` for pricing trends.
   - **Use Case**: Helps stakeholders understand overall cost structure and identify cost optimization opportunities.

2. **Usage Trends Dashboard**
   - **Purpose**: Track usage patterns and growth over time.
   - **Metrics**:
     - Total usage (DBUs, compute hours) over time (line chart).
     - Usage by team or tag (bar chart).
     - Usage by workspace or region (stacked bar chart).
     - Comparison of usage across time periods (line or bar chart).
   - **Data Source**: `system.billing.usage` for usage metrics; `system.compute.clusters` for compute-specific data.
   - **Use Case**: Identifies usage trends, seasonal patterns, and capacity planning needs.

3. **Object Usage Dashboard**
   - **Purpose**: Highlight usage and costs of specific objects (notebooks, clusters, jobs).
   - **Metrics**:
     - Usage by notebook (`usage_metadata.notebook_path`).
     - Cost by cluster (`usage_metadata.cluster_name`).
     - Cost by job (`usage_metadata.job_name`).
     - Top 10 most used objects (table or bar chart).
   - **Data Source**: `system.billing.usage` (using `usage_metadata` for object-specific data).
   - **Use Case**: Pinpoints high-cost or high-usage objects for optimization.

4. **Resource Utilization Dashboard**
   - **Purpose**: Monitor efficiency of compute and storage resources.
   - **Metrics**:
     - Cluster utilization (percentage of provisioned vs. used resources).
     - Storage usage trends (if available).
     - Job run frequency and duration.
     - Interactive session usage.
   - **Data Source**: `system.compute.clusters` for cluster metrics; `system.billing.usage` for storage costs.
   - **Use Case**: Identifies inefficiencies like idle clusters or oversized datasets.

5. **Anomaly Detection Dashboard**
   - **Purpose**: Detect unexpected spikes in usage or costs.
   - **Metrics**:
     - Usage/cost spikes (line chart with thresholds).
     - High-usage periods compared to historical averages.
   - **Data Source**: `system.billing.usage` with custom anomaly detection logic.
   - **Use Case**: Enables quick response to cost or usage anomalies.

6. **Cost Allocation Dashboard**
   - **Purpose**: Allocate costs across teams, projects, or workspaces.
   - **Metrics**:
     - Cost by team/project (using `custom_tags`).
     - Cost by workspace.
   - **Data Source**: `system.billing.usage` with tag-based filtering.
   - **Use Case**: Enhances transparency and accountability for cost management.

### Customization and Best Practices
- **Tagging**: Use custom tags in `system.billing.usage` to allocate costs by team, project, or other categories. Ensure resources like clusters and notebooks are tagged for accurate attribution.
- **Interactivity**: Include filters for time ranges, tags, users, or workspaces to allow stakeholders to explore data dynamically.
- **SQL Queries**: Use SQL queries to extract specific metrics. Example queries include:
  - Total cost by month.
  - Cost by SKU.
  - Usage by notebook or cluster.
  - Cost by team (via tags).
  - See the [sample queries](#xaiArtifact) for details.
- **Regular Updates**: Schedule dashboard refreshes to ensure up-to-date data.
- **Audience-Specific Dashboards**:
  - **Executive**: High-level metrics (total spend, key cost drivers, budget status).
  - **Technical**: Detailed resource usage and optimization insights.
  - **Team-Specific**: Tag-based cost allocation for team accountability.
- **Additional Data Sources**:
  - `system.access.audit` for user activity insights.
  - `system.compute.clusters` for compute optimization.
  - Check for ML-specific usage (e.g., MLflow) in `system.billing.usage`.

### Advanced Considerations
- **Trends**:
  - Monitor spend and usage growth, pricing changes, and seasonal patterns.
  - Use line charts to visualize trends over time.
- **User Activity**:
  - Track active users and top users by usage/cost using `system.access.audit`.
- **Compute Optimization**:
  - Analyze cluster idle time and auto-scaling effectiveness using `system.compute.clusters`.
- **Storage Costs**:
  - Track storage usage and costs if included in `system.billing.usage`.
- **ML Workloads**:
  - Explore MLflow usage metrics if available in system tables.

### Permissions and Retention
- **Permissions**: Users need SELECT permissions on `system.billing.usage` and `system.billing.list_prices`.
- **Retention**: Usage data is retained for 365 days; pricing data is stored indefinitely.

### Key Citations
- [Azure Databricks System Tables Documentation](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/)
- [AWS Databricks System Tables Documentation](https://docs.databricks.com/aws/en/admin/system-tables/)
- [Azure Databricks Billable Usage System Table](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/billing)
- [AWS Databricks Billable Usage System Table](https://docs.databricks.com/aws/en/admin/system-tables/billing)
- [AWS Databricks Usage Dashboards Guide](https://docs.databricks.com/aws/en/admin/account-settings/usage)
