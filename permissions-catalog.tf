import requests

# Configuration
DATABRICKS_HOST = "https://<workspace-url>.cloud.databricks.com"
PAT_TOKEN = "<personal-access-token>"
CATALOG_NAME = "<catalog-name>"
SERVICE_PRINCIPAL_ID = "<application-id>"

# API endpoint
url = f"{DATABRICKS_HOST}/api/2.0/permissions/catalogs/{CATALOG_NAME}"

headers = {
    "Authorization": f"Bearer {PAT_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "access_control_list": [{
        "service_principal_name": SERVICE_PRINCIPAL_ID,
        "permission_level": "MANAGE"
    }]
}

response = requests.put(url, json=payload, headers=headers)

if response.status_code == 200:
    print("Permission granted successfully")
else:
    print(f"Error {response.status_code}: {response.text}")
