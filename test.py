import requests
import json

url = "http://localhost:11434/api/generate"  # Ollama's API endpoint
headers = {"Content-Type": "application/json"}
data = {
    "model": "mistral:7b-instruct",  # Specify the model
    "prompt": "Write a short story about a cat",  # Your prompt
    "stream": False  # Set to True for streaming output
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())