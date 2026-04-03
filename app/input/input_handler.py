import uuid
from datetime import datetime

def handle_input(prompt: str):
    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt
    }