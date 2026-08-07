class EmbeddingService:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.0 for _ in text] for text in texts]
