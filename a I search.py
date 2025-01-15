from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

# Initialize the client
endpoint = "https://<your-service-name>.search.windows.net"
key = "<your-api-key>"
credential = AzureKeyCredential(key)
client = SearchIndexClient(endpoint=endpoint, credential=credential)

# List all indexes
result = client.list_indexes()
for index in result:
    print(f"Index name: {index.name}")
