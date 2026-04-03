import logging
from sentence_transformers import SentenceTransformer # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_model = None

def get_embedding_model():
    """Lazy load embedding model on first access."""
    global _model
    if _model is None:
        logger.info("Initializing embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model