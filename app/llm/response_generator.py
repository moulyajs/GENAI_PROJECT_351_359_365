import requests
import json
from app.utils.config import get_ollama_url

OLLAMA_URL = get_ollama_url()

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