from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Retrieve service credential
credential_provider = dbutils.credentials.getServiceCredentialsProvider('openai')
token_provider = lambda: credential_provider.get_token("https://search.azure.com/.default").token

# Initialize client
service_name = "<your-search-service>"
index_name = "<your-index>"
endpoint = f"https://{service_name}.search.windows.net/"
client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=token_provider
)

# Search query
results = client.search(search_text="quantum computing")
for result in results:
    print(result["title"])
