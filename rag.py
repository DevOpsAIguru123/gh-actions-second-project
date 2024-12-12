pip install python-dotenv azure-ai-formrecognizer azure-search-documents azure-core openai


import os
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndex
from azure.search.documents.indexes.models import SimpleField, SearchFieldDataType, SearchableField, VectorField
from azure.search.documents import SearchClient, IndexDocumentsBatch
from azure.search.documents.models import QueryVector
import openai

load_dotenv()  # Load environment variables from .env

# --- Load configuration ---
form_recognizer_endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
form_recognizer_key = os.getenv("FORM_RECOGNIZER_KEY")
search_endpoint = os.getenv("COGNITIVE_SEARCH_ENDPOINT")
search_key = os.getenv("COGNITIVE_SEARCH_KEY")
index_name = os.getenv("INDEX_NAME", "documents")

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
completion_model = os.getenv("AZURE_OPENAI_COMPLETION_MODEL", "gpt-4")

pdf_path = os.getenv("PDF_PATH", "sample.pdf")

# --- Step 1: Extract Text from PDF using Prebuilt Form Recognizer ---
document_analysis_client = DocumentAnalysisClient(
    endpoint=form_recognizer_endpoint,
    credential=AzureKeyCredential(form_recognizer_key)
)

print("Analyzing document with Form Recognizer...")
with open(pdf_path, "rb") as f:
    poller = document_analysis_client.begin_analyze_document("prebuilt-document", document=f)
result = poller.result()

extracted_text = []
for page_idx, page in enumerate(result.pages):
    for line in page.lines:
        extracted_text.append(line.content)

full_text = "\n".join(extracted_text)
print("Extracted text length:", len(full_text))

# Split text into chunks
# Simple approach: split by double newlines
chunks = [chunk.strip() for chunk in full_text.split("\n\n") if chunk.strip()]

# --- Step 2: Create or Update Azure Cognitive Search Index with Vector Field ---
index_client = SearchIndexClient(endpoint=search_endpoint, credential=AzureKeyCredential(search_key))

# We define a vector field for embeddings and a text field for content
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="content", type=SearchFieldDataType.String, searchable=True),
    VectorField(name="contentVector", searchable=True, dimensions=1536, vector_search_configuration="default")
]

my_index = SearchIndex(name=index_name, fields=fields)

print("Creating or updating index...")
try:
    index_client.create_or_update_index(my_index)
except Exception as e:
    print("Error creating index:", e)

search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=AzureKeyCredential(search_key))

# --- Step 3: Generate Embeddings for Document Chunks and Index them ---
def get_embedding(text):
    response = openai.Embedding.create(
        engine=embedding_model,
        input=text
    )
    return response["data"][0]["embedding"]

print("Generating embeddings and indexing documents...")
docs = []
for i, c in enumerate(chunks):
    embedding = get_embedding(c)
    docs.append({
        "id": str(i),
        "content": c,
        "contentVector": embedding
    })

batch = IndexDocumentsBatch.upload_documents(docs)
search_client.index_documents(batch)
print("Documents indexed with embeddings.")

# --- Step 4: Perform a Vector Search for the User Question ---
user_question = "What are the key topics discussed in the document?"
query_embedding = get_embedding(user_question)

search_results = search_client.search(
    search_text="",  # no keyword search
    vectors=[QueryVector(value=query_embedding, k=5, fields="contentVector")]
)

context_chunks = [res["content"] for res in search_results]

context_text = "\n".join(context_chunks)

# --- Step 5: Use GPT-4 for Generation with Context ---
prompt = f"""
You are a helpful assistant. Use the following context to answer the user question accurately and concisely.

Context:
{context_text}

User question: {user_question}

Answer:
"""

print("Sending prompt to Azure OpenAI (GPT-4)...")
completion = openai.Completion.create(
    engine=completion_model,
    prompt=prompt,
    max_tokens=500,
    temperature=0.2,
    stop=None
)

answer = completion.choices[0].text.strip()
print("Answer from GPT-4:\n", answer)