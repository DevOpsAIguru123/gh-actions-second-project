!pip install openai
%restart_python
from openai import OpenAI
import os

# Get token from notebook context
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

client = OpenAI(
    api_key=DATABRICKS_TOKEN,
    base_url="https://dbc-0a827284-a8d1.cloud.databricks.com/serving-endpoints"
)

response = client.chat.completions.create(
    model="databricks-meta-llama-3-3-70b-instruct",
    messages=[{"role": "user", "content": "What is an LLM agent?"}]
)

print(response.choices[0].message.content)
