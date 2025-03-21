import requests

# Replace with your Databricks instance URL and personal access token
DATABRICKS_HOST = "https://<your-databricks-instance>"
DATABRICKS_TOKEN = "<your-access-token>"

# API endpoint for listing users
url = f"{DATABRICKS_HOST}/api/2.0/preview/scim/v2/Users"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

# Make the GET request
response = requests.get(url, headers=headers)

if response.status_code == 200:
    users = response.json().get("Resources", [])
    for user in users:
        print(f"User ID: {user['id']}, Username: {user['userName']}")
else:
    print(f"Error: {response.status_code} - {response.text}")


import requests

# Replace with your Databricks instance URL and personal access token
DATABRICKS_HOST = "https://<your-databricks-instance>"
DATABRICKS_TOKEN = "<your-access-token>"

# API endpoint for listing users
url = f"{DATABRICKS_HOST}/api/2.0/preview/scim/v2/Users"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}

# Make the GET request
response = requests.get(url, headers=headers)

if response.status_code == 200:
    users = response.json().get("Resources", [])
    for user in users:
        print(f"User ID: {user['id']}, Username: {user['userName']}")
else:
    print(f"Error: {response.status_code} - {response.text}")

