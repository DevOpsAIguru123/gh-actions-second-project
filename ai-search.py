from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField
from azure.core.credentials import AzureKeyCredential

# Azure Search service configuration
service_name = "<your-service-name>"
admin_key = "<your-admin-key>"
endpoint = f"https://{service_name}.search.windows.net"
index_name = "sample-databricks-index"

# Create index client
index_client = SearchIndexClient(endpoint=endpoint, 
                               credential=AzureKeyCredential(admin_key))

# Define index schema
fields = [
    SimpleField(name="id", type="Edm.String", key=True, filterable=True),
    SimpleField(name="content", type="Edm.String", searchable=True)
]

# Create index
index = SearchIndex(name=index_name, fields=fields)
index_client.create_index(index)

# Create search client for uploading documents
search_client = SearchClient(endpoint=endpoint,
                           index_name=index_name,
                           credential=AzureKeyCredential(admin_key))

# Sample documents to upload
documents = [
    {
        "id": "doc1",
        "content": "This is a sample document from Databricks"
    },
    {
        "id": "doc2",
        "content": "Another test document for vector search"
    },
    {
        "id": "doc3",
        "content": "Third document with different content"
    }
]

# Upload documents
result = search_client.upload_documents(documents=documents)

# Print results
print(f"Uploaded {len(result)} documents")
