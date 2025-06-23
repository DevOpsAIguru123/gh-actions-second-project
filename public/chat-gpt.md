Awesome! I’ll explore how to create impactful Databricks dashboards using Databricks SQL and system tables on Azure, targeting managers as the primary stakeholders. I’ll focus on metrics tied to Unity Catalog usage, workspace-level activity, billing, and object access trends. I’ll also look into user and Genie activity, and any other insightful data points that can influence platform governance, optimization, or cost control.

I’ll get back to you with a detailed set of dashboard ideas and implementation guidance.


# Databricks Platform Usage Dashboards for Stakeholders

Databricks System Tables (in Unity Catalog) provide a rich source of operational and usage data that can be turned into insightful dashboards for stakeholders. Using Databricks SQL dashboards (or similar tools), you can visualize trends in platform usage, data access, and costs. Below are **key dashboard ideas** – each focusing on different aspects like cost, resource utilization, data usage, and user activity – to effectively communicate platform usage and value.

## Billing and Cost Analysis Dashboard

One of the most impactful areas for stakeholders is cost. A **Billing & Cost** dashboard can leverage the **Billable Usage** system table to track Databricks Unit (DBU) consumption and spending over time. This dashboard would highlight where costs are coming from and how they trend, enabling FinOps and budget control:

* **Overall DBU Usage & Cost Trend:** Show total DBUs consumed (and approximate cost) per day/week/month. This uses the `system.billing.usage` table, which breaks down DBU consumption across the account. Stakeholders can quickly see if usage (and hence cost) is increasing or within budget.
* **Cost by Workspace/Team/Tag:** If you have multiple workspaces or use tags, segment the cost by those. The usage records include fields like `workspace_id` and `custom_tags` for each usage record, so you can attribute spend to specific projects, departments, or environments (e.g. Prod vs Dev). This helps managers understand their team’s share of resource usage.
* **Cost by SKU or Service:** Break down usage by **SKU** (service tier) or workload type. For example, split out all-purpose compute vs. jobs compute vs. SQL warehouse usage using the `sku_name` or `billing_origin_product` in the usage data. This identifies which type of workload (interactive notebooks, jobs, SQL analytics, etc.) is driving the most cost.
* **Peak Usage and Forecast:** Visualize the peak daily usage and perform trend analysis for forecasting. Since the billing table has daily records, you can display a 30-day rolling trend and even project future usage. (For instance, Databricks’ own demos include dashboards for **billing forecast** using system tables.) Early warning charts can show if usage is spiking abnormally so that budget alerts can be set proactively.

By providing clear cost visuals and breakdowns, this dashboard ensures **financial transparency** and helps stakeholders in planning and optimizing Databricks spend.

## Compute Utilization and Efficiency Dashboard

To complement cost data, an **Infrastructure Utilization** dashboard focuses on how well the compute resources (clusters and SQL warehouses) are utilized. This helps identify inefficiencies (e.g. idle clusters) and opportunities to optimize performance vs. cost:

* **Cluster Runtime vs. CPU Utilization:** Using the **Clusters** and **Node Timeline** system tables, you can track each cluster’s configuration and its actual usage. The `system.compute.node_timeline` table records minute-by-minute utilization metrics (such as CPU usage) for each cluster node. A chart can show the average CPU% utilization per cluster versus its uptime or size. Low utilization clusters can be flagged (e.g. a cluster running 8 nodes at <20% CPU on average). This highlights wasted resources.
* **Underutilized Clusters Identification:** Build a table or chart listing clusters that have been running for long durations with low average CPU usage. For example, join `system.compute.clusters` (for cluster metadata like owner, size, creation time) with the aggregated `node_timeline` (for CPU metrics) to find clusters with many nodes but <20% CPU utilization. These are candidates for downscaling or auto-termination. Stakeholders can immediately see potential cost savings.
* **Auto-Termination and Idle Times:** Show which clusters are configured with auto-termination and which are not. A simple indicator or count of clusters without auto-termination (especially if they have long idle periods from audit logs) can drive policy changes. Similarly, visualize the distribution of idle time (e.g. longest idle periods) for running clusters.
* **SQL Warehouse Utilization:** If using Databricks SQL warehouses, include metrics from **SQL Warehouse Events** (`system.compute.warehouse_events`) such as how often warehouses scale up/down, start/stop events, and their uptime. This can be a timeline showing when each warehouse was running and at what size. Coupled with query volume, it shows if warehouses are sized correctly.

This dashboard focuses on **efficiency**: ensuring compute resources are right-sized and utilized. It speaks to both engineering (performance optimization) and finance (cost efficiency) stakeholders by illustrating where the platform can be tuned for better ROI.

## Workload and Performance Dashboard (Jobs & Queries)

Understanding what workloads are running – and how well they perform – is crucial for platform transparency. A **Workload Activity** dashboard covers scheduled jobs, pipelines, and ad-hoc queries, helping stakeholders see the platform’s productivity and reliability:

* **Job Runs Overview:** Use the **Lakehouse (Jobs) system tables** to chart job activity. For example, `system.lakeflow.job_run_timeline` provides start/end times for each job run, and `job_task_run_timeline` includes compute resource info. From these, show the number of job runs per day, success vs. failure counts, and average duration. Trends could reveal if more jobs are being onboarded or if failure rates are creeping up (warranting investigation).
* **Longest Running & Failing Jobs:** Identify the top N jobs by runtime and any chronic failing jobs. A table can list jobs that often exceed a certain duration or those with repeated failures (perhaps via the `job_tasks` table that tracks individual task outcomes). This helps in capacity planning and reliability improvement, as stakeholders can pinpoint which workflows might need attention or more resources.
* **SQL Query Metrics:** Leverage the **Query History** table which captures all SQL queries executed on warehouses or serverless endpoints. Key metrics to show include: total queries run per day (trend of interactive analytics usage), average query latency, and maybe 95th percentile execution time. You could also list the “top slow queries” or heavy users of the warehouse (by aggregating runtime or number of executions per user). This informs both the engineering team (for tuning slow queries) and product owners (to see adoption of analytics).
* **Resource Hotspots:** Combine job and query info with cluster/warehouse info to see if certain times of day have many concurrent jobs or queries. A heatmap of hour-of-day vs. activity level can reveal peak utilization periods. This can guide scheduling (to avoid too many jobs at the same hour) or scaling decisions for SQL endpoints during peak business hours.

By visualizing jobs and query performance, this dashboard highlights how the platform is being **used for data processing and analytics**, and whether it’s meeting SLAs. Stakeholders can derive insights on throughput (e.g., jobs per day) as well as quality (failure rates, slow query incidents) to ensure the platform supports business needs effectively.

## Unity Catalog Data Usage Dashboard

With Unity Catalog governing data assets, stakeholders often want to know **which data is being used and how**. An **Object Usage** dashboard can provide an overview of catalogs, schemas, tables, and their usage patterns:

* **Catalog/Schema Inventory:** List all catalogs and the number of schemas and tables in each (an overview of data assets). The SQL **Information Schema** views can be used here – for example, `system.information_schema.tables` lists all tables and views in a catalog. You could show counts of tables per schema or highlight new tables created in the last 7 days (by checking the `CREATION_TIME` or `LAST_ALTERED` timestamp). This gives a sense of growth of data assets in the workspace.
* **Most Active Tables/Views:** Use the **Table Lineage** logs to identify which datasets are accessed most frequently. The `system.access.table_lineage` table logs every read or write on Unity Catalog tables. By grouping events by table, you can rank the “top 10 most queried tables” in the last month. This shows stakeholders which data is critical or popular. Conversely, it can also show tables *never* accessed in a given period – potential candidates for archiving to save costs.
* **Usage by Catalog/Workspace:** If you have multiple catalogs (e.g., departmental data domains), compare their usage. A bar chart could show each catalog’s total query count or read volume (from lineage records) to see which domains are most active. You can also filter the dashboard to a specific catalog (as requested) to drill down into one area: see all schemas, tables, and who’s querying them. This is useful for data owners to monitor their domain.
* **Data Access Trends:** Plot how data access is growing over time. For instance, total read events per week (from lineage) or number of distinct tables used per week. An increasing trend might indicate broader adoption of the lakehouse, whereas a stagnant usage of certain data might prompt investigation (are users not finding a dataset useful?).

By focusing on **Unity Catalog usage**, this dashboard ties platform activity back to data assets and governance. It ensures data stewards and stakeholders see real value (or underutilization) of the data in the lakehouse, and can drive decisions on data curation, archival, or optimization.

## User Activity and Audit Dashboard

Understanding **who** is using the platform and what they are doing is key for both engagement and governance. A **User Activity** dashboard uses audit logs and usage metrics to give a people-centric view of the platform:

* **Active Users and Logins:** Track the number of active users over time (daily or monthly active users) by counting distinct user IDs in the audit logs or query history. The **Audit Logs** (`system.access.audit`) record all kinds of events including user logins and actions. A chart of daily login events or active user count indicates adoption trends – stakeholders can see if platform usage is spreading across teams or if it’s concentrated to a few users.
* **User Engagement Metrics:** Show which users or teams are running the most commands, queries, or jobs. For example, rank users by the number of queries run (from Query History) or by compute resources consumed (from Billable Usage’s identity metadata). This highlights power users and can also identify if any users might need more support or training (if they have errors). According to real-world monitoring, usage logs let you see which users are active and **which features they use** on Databricks – e.g. some may primarily use notebooks, others SQL, others automated jobs.
* **Databricks Assistant (GenAI) Queries:** If your stakeholders are interested in the new AI assistant (“Genie”) usage, include a panel for it. The **Databricks Assistant events** table tracks every user question asked to the AI assistant. You can show how many questions were asked via the assistant per week, which users use it most, and possibly categorize the queries. This gives insight into adoption of AI/BI Genie and its impact on productivity (for example, a rising trend might show users find it useful for self-service BI).
* **Important Audit Events:** Include any notable security or governance events: e.g. number of permission changes, changes to Unity Catalog privileges, or **outbound network** access denials (`system.access.outbound_network`) if relevant. While not central to usage, showing that audit capabilities are in place (and no anomalies detected) can reassure stakeholders from a compliance perspective. You might also track high-level counts like “number of notebooks created” or “distinct new jobs created” as a proxy for user-driven content creation on the platform (these could be derived from audit events as well).

This dashboard serves both **user adoption** and **audit oversight** purposes. By seeing who is doing what (and how much), executives and platform owners can gauge the platform’s reach in the organization and ensure it’s being used in accordance with policies. It also highlights the human angle of your Databricks usage – celebrating power users or identifying training needs.

## Additional Considerations and Trends

Beyond the core areas above, there are other metrics and dashboards you might consider for impact:

* **Model Serving Usage:** If you leverage Databricks Model Serving, you could track endpoint invocations. The `system.serving.endpoint_usage` table (in preview) logs each request’s token count and other details. A dashboard could show which ML endpoints are most active and how usage is growing, which is valuable for AI product stakeholders.
* **Data Lineage and Quality:** Going deeper into lineage, the **Column Lineage** table logs column-level read/write events. A dashboard might visualize data flow: e.g., which upstream tables feed into a given table, or how widely a critical column is used across notebooks. While more for internal engineering use, this can demonstrate robust governance to stakeholders.
* **Service Health/SLA Dashboard:** Using query timelines and job runtimes, one can also create an SLA view – e.g., what percent of jobs complete within expected time, or how often critical pipelines miss their schedule. If stakeholders are concerned with reliability, this is impactful.
* **Executive Summary:** Finally, consider a **summary dashboard** that pulls key KPIs from all the above into one view for executives. For example: *Total monthly spend vs. budget, Number of active users this month, Total jobs run, Top 3 most used datasets,* etc. This high-level dashboard can be the starting point, with the other detailed dashboards linked or available for drill-down. This way, stakeholders get a snapshot of platform value at a glance, with the ability to explore further details as needed.

Each of these dashboards is made possible by Databricks’ system tables and information schema, which together provide a comprehensive picture of your Lakehouse usage. By mixing and matching these metrics, you can deliver **impactful insights** – from cost savings opportunities to compliance assurance – that resonate with both technical and business stakeholders. The goal is to demonstrate how the Databricks platform is being utilized and to inform decisions on optimization and governance. With the right dashboards in place, stakeholders will have a data-driven window into the platform’s operation and the benefits it’s delivering to the organization.

**Sources:**

* Databricks System Tables Documentation – *Monitor account activity with system tables*
* Databricks System Tables Documentation – *List of available system tables*
* Databricks SQL Information Schema – *Metadata views for catalogs and tables*
* Medium (Databricks Platform SME) – *Cost Optimization via System Tables*
* DataSturdy Blog – *Using system tables for cluster utilization and audit*
* Azure Databricks Documentation – *Billable usage table schema* (fields like workspace\_id, custom\_tags)
* Azure Databricks Documentation – *Table lineage and audit events*
