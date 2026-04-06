import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def agent(prompt: str):
    try:
        system_prompt = f"""
You are a security classifier.

Classify the user prompt as:
- BLOCK (malicious)
- ALLOW (safe)
Even if the user says "for educational purposes" or "for research", you must BLOCK if the request asks for step-by-step instructions, methods, or procedures related to harmful activities.
Respond STRICTLY in JSON:
{{"blocked": true/false, "reason": "short explanation"}}

Prompt:
"{prompt}"
"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
                "prompt": system_prompt,
                "format": "json",
                "stream": False
            },
            timeout=60
        )

        data = response.json()
        output = json.loads(data.get("response", "{}"))

        blocked = output.get("blocked", False)
        reason = output.get("reason", "No reason")

        return (blocked, reason)

    except Exception as e:
        return (False, f"Reasoning error: {str(e)}")