data "databricks_spark_version" "latest" {
  long_term_support = true
}


resource "databricks_cluster_policy" "cluster_policies" {
  for_each = var.cluster_policy_configs

  name = "${each.key}_cluster_policy"
  definition = jsonencode(merge(
    {
      "spark_version": {
        "type": "fixed",
        "value": data.databricks_spark_version.latest.id
      },
      "node_type_id": {
        "type": "allowlist",
        "values": each.value.allowed_node_types,
        "defaultValue": each.value.default_node_type
      },
      "driver_node_type_id": {
        "type": "allowlist",
        "values": each.value.allowed_node_types,
        "defaultValue": each.value.default_node_type
      },
      "autoscale.min_workers": {
        "type": "fixed",
        "value": each.value.autoscale_min_workers
      },
      "autoscale.max_workers": {
        "type": "fixed",
        "value": each.value.autoscale_max_workers
      },
      "runtime_engine": {
        "type": "fixed",
        "value": each.value.runtime_engine,
        "hidden": each.value.runtime_engine_hidden
      },
      "custom_tags.team": {
        "type": "fixed",
        "value": each.value.custom_tags["team"]
      },
      "custom_tags.environment": {
        "type": "fixed",
        "value": each.value.custom_tags["environment"]
      },
    },
    # Only include autotermination for all-purpose clusters
    each.value.cluster_type == "all-purpose" ? {
      "autotermination_minutes": {
        "type": "fixed",
        "value": each.value.autotermination_minutes
      }
    } : {}
  ))
}