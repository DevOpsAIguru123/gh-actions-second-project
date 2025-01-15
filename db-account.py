import requests

def list_network_configurations(account_id, api_token):
    url = f"https://accounts.cloud.databricks.com/api/2.0/accounts/{account_id}/network-connectivity"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()