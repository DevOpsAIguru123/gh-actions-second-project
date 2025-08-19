# --- params ---
INACTIVITY_DAYS = 90
WORKSPACE_ID = "633686803665557"   # your workspace
GROUP_NAME = "marketing_power_users"  # <-- exact group name as seen in Admin UI

from pyspark.sql.functions import col, lower, max as max_, current_timestamp, datediff, when, lit
from pyspark.sql import Row

# 1) All workspace users (normalized)
users_df = spark.sql("SHOW USERS").select(lower(col("name")).alias("user"))

# 1a) Keep only members of the target group (direct or nested)
#     We iterate users and test membership with: SHOW GROUPS WITH USER `<user>`
user_list = [r.user for r in users_df.collect()]

group_members = []
for u in user_list:
    # This returns rows: name (group), directGroup (bool) — includes nested paths
    groups_for_user = spark.sql(f"SHOW GROUPS WITH USER `{u}`").select("name").collect()
    if any(r.name == GROUP_NAME for r in groups_for_user):
        group_members.append(Row(user=u))

group_members_df = spark.createDataFrame(group_members) if group_members else spark.createDataFrame([], "user string")

# 1b) Users in BOTH: workspace roster ∩ target group
scoped_users = users_df.join(group_members_df, "user", "inner")

# 2) Login events from audit logs (workspace-scoped)
login_actions = ["login", "aadBrowserLogin", "aadTokenLogin", "jwtLogin"]
logins = (
    spark.table("system.access.audit")
      .where(col("service_name") == "accounts")
      .where(col("action_name").isin(*login_actions))
      .where(col("workspace_id") == lit(WORKSPACE_ID))
      .select(lower(col("user_identity.email")).alias("user"), col("event_time"))
)
last_login = logins.groupBy("user").agg(max_("event_time").alias("last_login_utc"))

# 3) Inactive within the target group
inactive = (
    scoped_users.join(last_login, "user", "left")
      .withColumn("inactive_days",
                  when(col("last_login_utc").isNull(), lit(None))
                  .otherwise(datediff(current_timestamp(), col("last_login_utc"))))
      .withColumn("status",
                  when(col("last_login_utc").isNull(), lit("never_logged_in"))
                  .when(col("inactive_days") >= lit(INACTIVITY_DAYS), lit("inactive"))
                  .otherwise(lit("active_recent")))
      .filter(col("status").isin("never_logged_in", "inactive"))
      .orderBy(col("last_login_utc").asc_nulls_first())
)

display(inactive.select("user", "last_login_utc", "inactive_days", "status"))
