resource "databricks_job" "example_job" {
  name = "Example Job with Cluster Policy"

  job_cluster {
    job_cluster_key = "main_cluster"
    new_cluster {
      policy_id = data.databricks_cluster_policy.existing_policy.id
      num_workers = 2
      spark_version = "11.3.x-scala2.12"
      node_type_id = "Standard_DS3_v2"
    }
  }

  task {
    task_key = "main_task"

    notebook_task {
      notebook_path = "/path/to/your/notebook"
    }

    job_cluster_key = "main_cluster"
  }
}
