environment = "dev"

cluster_policy_configs = {
  team1_all_purpose = {
    cluster_type            = "all-purpose"
    allowed_node_types     = ["Standard_DS3_v2"]
    default_node_type      = "Standard_DS3_v2"
    autotermination_minutes = 60
    autoscale_min_workers  = 1
    autoscale_max_workers  = 1
    runtime_engine         = "STANDARD"
    runtime_engine_hidden  = true
    custom_tags            = {
      team = "team1"
      environment = "dev"
    }
  }
  team2_job_compute = {
    cluster_type            = "job"
    allowed_node_types     = ["Standard_DS3_v2"]
    default_node_type      = "Standard_DS3_v2"
    autoscale_min_workers  = 1
    autoscale_max_workers  = 1
    runtime_engine         = "STANDARD"
    runtime_engine_hidden  = true
    custom_tags            = {
      team = "team2"
      environment = "dev"
    }
  }
}