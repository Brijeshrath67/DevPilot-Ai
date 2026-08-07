from typing import List

class EmbeddingService:
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [[0.0 for _ in text] for text in texts]
