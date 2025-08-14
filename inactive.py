INACTIVITY_DAYS = 90
WORKSPACE_ID = "633686803665557"  # replace with your workspace ID

from pyspark.sql.functions import col, lower, max as max_, current_timestamp, datediff, when, lit

# 1) All workspace users
users_df = spark.sql("SHOW USERS").select(lower(col("name")).alias("user"))

# 2) Login events from audit logs
login_actions = ["login", "aadBrowserLogin", "aadTokenLogin", "jwtLogin"]

logins = (
    spark.table("system.access.audit")
      .where(col("service_name") == "accounts")
      .where(col("action_name").isin(*login_actions))
      .where(col("workspace_id") == lit(WORKSPACE_ID))
      .select(lower(col("user_identity.email")).alias("user"), col("event_time"))
)

last_login = logins.groupBy("user").agg(max_("event_time").alias("last_login_utc"))

# 3) Flag inactive users
inactive = (
    users_df.join(last_login, "user", "left")
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
