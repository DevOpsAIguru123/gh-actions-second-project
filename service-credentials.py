from openai import AzureOpenAI

# Retrieve and configure the service credential
credential_provider = dbutils.credentials.getServiceCredentialsProvider('openai')

# Create a callable token provider function
token_provider = lambda: credential_provider.get_token("https://cognitiveservices.azure.com/.default").token

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint="https://azure-openai-vvvv.openai.azure.com/",
    api_version="2024-02-15-preview",
    azure_ad_token_provider=token_provider
)

# Query the model
response = client.chat.completions.create(
    model="gpt-4o",  # Use your Azure deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Explain quantum computing"}
    ]
)

print(response.choices[0].message.content)
