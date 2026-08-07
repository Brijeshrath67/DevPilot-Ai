from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService


class RepositoryChatAgent(BaseAgent):
    def __init__(self, llm_service: LLMService, vector_service: VectorService):
        self.llm_service = llm_service
        self.vector_service = vector_service

    def handle(self, payload: dict) -> dict:
        question = payload.get("question", "")
        context = self.vector_service.query_vectors(question)
        answer = self.llm_service.generate(f"Answer question with context: {context}")
        return {"answer": answer, "provenance": []}
