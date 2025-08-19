# === params ===
INACTIVITY_DAYS = 90
WORKSPACE_ID    = "633686803665557"
GROUP_NAME      = "marketing_power_users"

USE_ACCOUNT_SCIM = True   # True = Account Groups API (recommended with Automatic identity)
ACCOUNT_ID       = "<your_databricks_account_id>"
ACCOUNT_HOST     = "https://accounts.azuredatabricks.net"  # account console host

# If you prefer workspace-level SCIM (older/legacy), set USE_ACCOUNT_SCIM=False and:
WORKSPACE_HOST   = "https://<your-workspace-host>"         # e.g., https://adb-xxx.azuredatabricks.net

# Store your PAT in a secret scope; don’t hardcode.
TOKEN = dbutils.secrets.get("my-scope", "DATABRICKS_PAT")

import requests, math
from pyspark.sql.functions import col, lower, max as max_, current_timestamp, datediff, when, lit
from pyspark.sql import Row

def scim_get(path, params=None):
    base = f"{ACCOUNT_HOST}/api/2.0/accounts/{ACCOUNT_ID}/scim/v2" if USE_ACCOUNT_SCIM else f"{WORKSPACE_HOST}/api/2.0/preview/scim/v2"
    r = requests.get(base + path, headers={"Authorization": f"Bearer {TOKEN}"}, params=params or {}, timeout=30)
    r.raise_for_status()
    return r.json()

def get_group_by_name(name):
    # SCIM filter by displayName; exact match with eq
    js = scim_get("/Groups", params={"filter": f'displayName eq "{name}"'})
    resources = js.get("Resources", [])
    return resources[0] if resources else None

def get_user_email(user_id):
    js = scim_get(f"/Users/{user_id}")
    # SCIM uses userName for the login/email
    return js.get("userName")

def expand_group_members(group_obj):
    """Recursively expand nested groups to a set of user emails."""
    users, stack = set(), [group_obj]
    seen_groups = set()
    while stack:
        g = stack.pop()
        if not g or g.get("id") in seen_groups:
            continue
        seen_groups.add(g.get("id"))
        for m in g.get("members", []) or []:
            if m.get("type") == "User":
                email = get_user_email(m["value"])
                if email:
                    users.add(email.lower())
            elif m.get("type") == "Group":
                sub = scim_get(f"/Groups/{m['value']}")
                stack.append(sub)
    return users

# 1) fetch members of the target group (including nested)
grp = get_group_by_name(GROUP_NAME)
assert grp, f"Group not found: {GROUP_NAME}"
emails = expand_group_members(grp)
group_users_df = spark.createDataFrame([Row(user=e) for e in sorted(emails)])

# 2) last-login calculation (your original logic, scoped to workspace)
login_actions = ["login","aadBrowserLogin","aadTokenLogin","jwtLogin"]
logins = (
    spark.table("system.access.audit")
      .where(col("service_name") == "accounts")
      .where(col("action_name").isin(*login_actions))
      .where(col("workspace_id") == lit(WORKSPACE_ID))
      .select(lower(col("user_identity.email")).alias("user"), col("event_time"))
)
last_login = logins.groupBy("user").agg(max_("event_time").alias("last_login_utc"))

# 3) inactive within that group only
inactive = (
    group_users_df.join(last_login, "user", "left")
      .withColumn("inactive_days",
                  when(col("last_login_utc").isNull(), lit(None))
                  .otherwise(datediff(current_timestamp(), col("last_login_utc"))))
      .withColumn("status",
                  when(col("last_login_utc").isNull(), lit("never_logged_in"))
                  .when(col("inactive_days") >= lit(INACTIVITY_DAYS), lit("inactive"))
                  .otherwise(lit("active_recent")))
      .filter(col("status").isin("never_logged_in","inactive"))
      .orderBy(col("last_login_utc").asc_nulls_first())
)

display(inactive.select("user","last_login_utc","inactive_days","status"))
