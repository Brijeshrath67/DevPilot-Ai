from typing import Any, List

class RAGSkill:
    def __init__(self, vector_service: Any, embedding_service: Any):
        self.vector_service = vector_service
        self.embedding_service = embedding_service

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Any]:
        return self.vector_service.query_vectors(query, top_k=top_k)

    def build_prompt(self, question: str, context: List[Any]) -> str:
        return f"Use the following context to answer the question: {question}"
