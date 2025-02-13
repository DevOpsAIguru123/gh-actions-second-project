
# pip install azure-ai-formrecognizer
import os
import time
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Set these variables with your Azure Document Intelligence details
endpoint = "https://docintel.cognitiveservices.azure.com/"
api_key = ""

# Path to your PDF document to analyze
pdf_path = "pdf_sample.pdf"

# Path for output text file
output_txt = "extracted_text.txt"

# Create a DocumentAnalysisClient
document_client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key)
)

# Choose the prebuilt model for layout extraction.
# You can also use prebuilt-invoice, prebuilt-businessCard, etc.
model_id = "prebuilt-document"

# Open the PDF file in binary mode
with open(pdf_path, "rb") as fd:
    poller = document_client.begin_analyze_document(
        model_id,
        document=fd
    )
    result = poller.result()

# Initialize an empty list to collect extracted text lines
extracted_lines = []

# The result includes pages and their extracted content.
for page in result.pages:
    # Each page includes lines and words; here we collect the full text line by line.
    for line in page.lines:
        extracted_lines.append(line.content)

# Optionally, you can also process tables or key-value pairs if needed.

# Write the extracted text into a text file.
with open(output_txt, "w", encoding="utf-8") as f:
    for line in extracted_lines:
        f.write(line + "\n")

print(f"Extracted text has been written to {output_txt}")
