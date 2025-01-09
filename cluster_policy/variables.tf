variable "environment" {
  description = "Environment (dev, test, prod)"
  type        = string
}


variable "cluster_policy_configs" {
  description = "Map of environment and purpose-specific cluster policy configurations"
  type = map(object({
    cluster_type            = string
  #  spark_version_prefix   = string
    allowed_node_types     = list(string)
    default_node_type      = string
    autotermination_minutes = optional(number)
    autoscale_min_workers  = number
    autoscale_max_workers  = number
    runtime_engine         = string
    runtime_engine_hidden  = bool
    custom_tags            = map(string)
  }))
}