import msal
import requests

# ---------- Configuration ----------
client_id = "<SERVICE_PRINCIPAL_APP_ID>"
client_secret = "<SERVICE_PRINCIPAL_SECRET>"
tenant_id = "<YOUR_TENANT_ID>"
account_id = "<YOUR_DATABRICKS_ACCOUNT_ID>"
# Replace with your correct Databricks accounts API base URL
base_url = "https://accounts.azuredatabricks.net"
authority = f"https://login.microsoftonline.com/{tenant_id}"
scope = ["https://management.azure.com/.default"]
# -----------------------------------

# Step 1: Acquire an access token using service principal credentials
app = msal.ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret,
)

token_response = app.acquire_token_for_client(scopes=scope)
if "access_token" not in token_response:
    raise Exception("Failed to obtain access token: " + str(token_response))

access_token = token_response["access_token"]

# Step 2: Call the Databricks Account Users API
endpoint_url = f"{base_url}/api/2.0/accounts/{account_id}/users"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.get(endpoint_url, headers=headers)
if response.status_code == 200:
    users = response.json()
    print("Account Users:")
    print(users)
else:
    print(f"Error {response.status_code}: {response.text}")
