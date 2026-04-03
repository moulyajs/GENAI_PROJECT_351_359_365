import json
import logging
from typing import List, Tuple, Callable
import numpy as np

logger = logging.getLogger(__name__)

# Cosine Similarity computation
def cosine_similarity(v1: np.ndarray, v2_matrix: np.ndarray) -> np.ndarray:
    if v2_matrix.size == 0 or v1.size == 0: 
        return np.array([])
    dot_product = np.dot(v2_matrix, v1)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2_matrix, axis=1)
    return dot_product / (norm_v1 * norm_v2 + 1e-10)

class VectorDB:

    # Initialize vector database
    def __init__(self):
        self.malicious_prompts = []
        self.safe_prompts = []
        self.malicious_embeddings = np.array([])
        self.safe_embeddings = np.array([])
        self.is_initialized = False

    # Load knowledge base
    def load_knowledge_base(self, malicious_path: str, safe_path: str) -> None:
        logger.info(f"Loading datasets from {malicious_path} and {safe_path}")

        try:
            with open(malicious_path, 'r', encoding='utf-8') as f:
                self.malicious_prompts = json.load(f)
            with open(safe_path, 'r', encoding='utf-8') as f:
                self.safe_prompts = json.load(f)
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            self.malicious_prompts = []
            self.safe_prompts = []
            
        self._standardize_prompts()
        
    # Standardize prompts
    def _standardize_prompts(self) -> None:
        if self.malicious_prompts and isinstance(self.malicious_prompts[0], dict):
            self.malicious_prompts = [item.get('prompt', item.get('text', '')) for item in self.malicious_prompts]
        if self.safe_prompts and isinstance(self.safe_prompts[0], dict):
            self.safe_prompts = [item.get('prompt', item.get('text', '')) for item in self.safe_prompts]

    # Build index
    def build_index(self, embedding_func: Callable[[List[str]], np.ndarray]) -> None:
        if not self.malicious_prompts and not self.safe_prompts:
            logger.warning("Empty datasets. Cannot build vector index.")
            return

        logger.info("Computing embeddings for malicious prompts...")
        if self.malicious_prompts:
            self.malicious_embeddings = embedding_func(self.malicious_prompts)
        
        logger.info("Computing embeddings for safe prompts...")
        if self.safe_prompts:
            self.safe_embeddings = embedding_func(self.safe_prompts)
        
        self.is_initialized = True
        logger.info("Vector index built successfully.")

    # Retrieve context
    def retrieve_context(self, query_vector: np.ndarray, top_k: int = 2, min_score: float = 0.4) -> Tuple[List[str], List[str], float, float]:
        if not self.is_initialized or query_vector.size == 0:
            return [], [], 0.0, 0.0

        malicious_contexts = []
        max_malicious_score = 0.0

        if self.malicious_embeddings.size > 0:
            malicious_scores = cosine_similarity(query_vector, self.malicious_embeddings)

            if malicious_scores.size > 0:
                max_malicious_score = float(np.max(malicious_scores))
                valid_idx = np.where(malicious_scores >= min_score)[0]
                
                if valid_idx.size > 0:
                    valid_scores = malicious_scores[valid_idx]
                    sorted_valid_idx = valid_idx[np.argsort(valid_scores)[::-1]]
                    actual_k = min(top_k, sorted_valid_idx.size)
                    top_idx = sorted_valid_idx[:actual_k]
                    malicious_contexts = [self.malicious_prompts[i] for i in top_idx]

        safe_contexts = []
        max_safe_score = 0.0

        if self.safe_embeddings.size > 0:
            safe_scores = cosine_similarity(query_vector, self.safe_embeddings)
            if safe_scores.size > 0:
                max_safe_score = float(np.max(safe_scores))
                valid_idx = np.where(safe_scores >= min_score)[0]

                if valid_idx.size > 0:
                    valid_scores = safe_scores[valid_idx]
                    sorted_valid_idx = valid_idx[np.argsort(valid_scores)[::-1]]
                    actual_k = min(top_k, sorted_valid_idx.size)
                    top_idx = sorted_valid_idx[:actual_k]
                    safe_contexts = [self.safe_prompts[i] for i in top_idx]

        return malicious_contexts, safe_contexts, max_malicious_score, max_safe_score
