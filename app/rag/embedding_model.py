import logging
import numpy as np
from typing import List
from app.utils.config import get_embedding_model

logger = logging.getLogger(__name__)

class EmbeddingModel:

    # Initialize EmbeddingModel
    def __init__(self):
        logger.info("Initializing EmbeddingModel using global model.")
        self.model = get_embedding_model()
        
    # Generate embedding
    def generate_embedding(self, text: str) -> np.ndarray:
        if not text.strip():
            return np.array([])
        return self.model.encode(text, convert_to_numpy=True)
        
    # Generate batch embeddings
    def generate_batch_embeddings(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([])
        return self.model.encode(texts, convert_to_numpy=True)
