import requests
import json
# import os # If using docker to get env

OLLAMA_URL = "http://localhost:11434/api/generate" # For local run
# OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/generate" # For docker

def generate_response(prompt: str) -> str:
    try:
        safe_prompt = f"""
You are a helpful assistant.

Answer the user clearly and concisely.

User: {prompt}
Assistant:
"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
                "prompt": safe_prompt,
                "stream": False
            },
            timeout=300
        )

        data = response.json()

        # Debug
        print("RAW OLLAMA RESPONSE:", data)

        output = data.get("response")

        if not output:
            return "Empty response from TinyLlama"

        return output.strip()

    except Exception as e:
        return f"Error generating response: {str(e)}"