import requests
import json

# Get user context token and host
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
#host = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

url = f"https://dbc-0a827284-a8d1.cloud.databricks.com/serving-endpoints/databricks-meta-llama-3-3-70b-instruct/invocations"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "messages": [
        {
            "role": "user",
            "content": "What is an LLM agent?"
        }
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.content)
