curl -X POST "https://<YOUR_AZURE_OPENAI_ENDPOINT>/openai/deployments/<YOUR_DEPLOYMENT_NAME>/chat/completions?api-version=2023-12-01-preview" \
     -H "Content-Type: application/json" \
     -H "api-key: <YOUR_API_KEY>" \
     -d '{
          "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
          ],
          "max_tokens": 100
        }'