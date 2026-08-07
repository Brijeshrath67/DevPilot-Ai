import hashlib
import math

DEFAULT_DIMENSION = 384


class EmbeddingService:
    """Deterministic, dependency-free embedding generator.

    Produces a stable 384-dimensional unit vector per text so Pinecone and other
    vector stores receive consistent, queryable embeddings without requiring a
    model download or API key at runtime.
    """

    def __init__(self, dimension: int = DEFAULT_DIMENSION) -> None:
        self.dimension = dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]

    def embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for index, char in enumerate(text):
            digest = hashlib.md5(f"{index}:{char}".encode()).digest()  # noqa: S324  # deterministic hash, not security
            bucket = int.from_bytes(digest[:2], "big") % self.dimension
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[bucket] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [round(value / norm, 6) for value in vector]
