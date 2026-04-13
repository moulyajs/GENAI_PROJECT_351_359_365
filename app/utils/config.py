import logging
import os
from sentence_transformers import SentenceTransformer # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_model = None

# Lazy load embedding model on first access.
def get_embedding_model():
    global _model
    if _model is None:
        logger.info("Initializing embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

# Get the Ollama URL based on the environment (local vs docker).
def get_ollama_url():
    # Docker uses OLLAMA_HOST environment variable (e.g., http://host.docker.internal:11434)
    # Local fallback is http://localhost:11434
    
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    return f"{host.rstrip('/')}/api/generate"