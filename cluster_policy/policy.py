import requests

# Databricks workspace information
DATABRICKS_WORKSPACE_URL = "<your_databricks_workspace_url>"  # Example: "https://adb-xxxx.azuredatabricks.net"
DATABRICKS_TOKEN = "<your_personal_access_token>"

# Filter parameter
SERVICE_PRINCIPAL_ID = "<service_principal_id>"
CLUSTER_POLICY_ID = "<your_cluster_policy_id>"
CLUSTER_ID = "<cluster_id>"  # If you're reusing an existing cluster

# Headers for REST API
HEADERS = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}


def get_all_jobs():
    """Fetch all jobs (workflows) from the Databricks workspace."""
    jobs_url = f"{DATABRICKS_WORKSPACE_URL}/api/2.1/jobs/list"
    response = requests.get(jobs_url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("jobs", [])
    else:
        raise Exception(f"Error fetching jobs: {response.text}")


def update_job_with_cluster_policy(job_id):
    """Update a Databricks job with the specified cluster policy."""
    update_url = f"{DATABRICKS_WORKSPACE_URL}/api/2.1/jobs/reset"
    
    payload = {
        "job_id": job_id,
        "new_settings": {
            "name": f"Updated-Workflow-{job_id}",
            "tasks": [{
                "task_key": "main_task",
                "existing_cluster_id": CLUSTER_ID,
                "cluster_spec": {
                    "policy_id": CLUSTER_POLICY_ID
                }
            }]
        }
    }

    response = requests.post(update_url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        print(f"Successfully updated job ID {job_id} with cluster policy.")
    else:
        print(f"Failed to update job ID {job_id}. Error: {response.text}")


def main():
    """Main function to fetch jobs and apply the cluster policy."""
    print("Fetching all Databricks jobs...")
    jobs = get_all_jobs()
    print(f"Total jobs found: {len(jobs)}")

    for job in jobs:
        if job.get("creator_user_name") == SERVICE_PRINCIPAL_ID:
            print(f"Assigning cluster policy to job ID: {job['job_id']}")
            update_job_with_cluster_policy(job["job_id"])


if __name__ == "__main__":
    main()