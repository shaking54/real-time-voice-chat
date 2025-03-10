import os
import requests
import json

#OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
OLLAMA_API_URL = "https://6a7c-34-16-190-7.ngrok-free.app/api/generate"

def processing_output(response):

    response_text = ""
    for line in response.split("\n"):
        print(line)
        try:
            data = json.loads(line.strip())
            response_text += data["response"]
        except json.JSONDecodeError:
            continue  # Ignore lines that are not valid JSON
    
    return response_text

def fake_generate_response(prompt):
    return prompt

def generate_response(prompt):
    
    try:
        response = requests.post(OLLAMA_API_URL, json={'model': 'mistral', 'prompt': prompt})
        response_data = processing_output(response.text)
        return response_data
    
    except Exception as e:
        print(f"Error in LLM: {e}")
        return None


if __name__ == '__main__':
    prompt = "Hello, how are you?"
    print(generate_response(prompt))
