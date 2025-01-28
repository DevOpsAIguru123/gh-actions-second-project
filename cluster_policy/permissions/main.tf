# Data sources to look up cluster and policy IDs
data "databricks_cluster" "clusters" {
  for_each = var.cluster_and_policy_permissions_variables
  
  cluster_name = each.value.cluster_name
}

data "databricks_cluster_policy" "policies" {
  for_each = {
    for key, value in var.cluster_and_policy_permissions_variables :
    key => value if value.cluster_policy_permissions != null
  }
  
  name = each.value.cluster_policy_name
}

# Databricks cluster permissions
resource "databricks_permissions" "cluster_permissions" {
  for_each = var.cluster_and_policy_permissions_variables

  cluster_id = data.databricks_cluster.clusters[each.key].id

  dynamic "access_control" {
    for_each = split(",", each.value.cluster_permissions)
    content {
      group_name       = each.value.team_ad_group_name
      permission_level = access_control.value
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Databricks cluster policy permissions
resource "databricks_permissions" "policy_permissions" {
  for_each = {
    for key, value in var.cluster_and_policy_permissions_variables :
    key => value if value.cluster_policy_permissions != null
  }

  cluster_policy_id = data.databricks_cluster_policy.policies[each.key].id

  dynamic "access_control" {
    for_each = split(",", each.value.cluster_policy_permissions)
    content {
      group_name       = each.value.team_ad_group_name
      permission_level = access_control.value
    }
  }

  lifecycle {
    prevent_destroy = true
  }
} 