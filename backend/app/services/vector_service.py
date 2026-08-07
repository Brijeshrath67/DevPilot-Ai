from typing import Any, List

class VectorService:
    def upsert_vectors(self, vectors: List[Any]) -> None:
        pass

    def query_vectors(self, query: str, top_k: int = 5) -> List[Any]:
        return []
