from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# Retrieve service credential
credential_provider = dbutils.credentials.getServiceCredentialsProvider('openai')
token_provider = lambda: credential_provider.get_token("https://cognitiveservices.azure.com/.default").token

# Initialize client
endpoint = "https://<your-document-intelligence-resource>.cognitiveservices.azure.com/"
client = DocumentIntelligenceClient(
    endpoint=endpoint,
    credential=token_provider
)

# Analyze document
with open("invoice.pdf", "rb") as f:
    poller = client.begin_analyze_document(
        model_id="prebuilt-invoice",
        analyze_request=f
    )
    result = poller.result()
    print(result.documents[0].fields.get("Total").value)
