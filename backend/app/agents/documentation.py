from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService


class DocumentationAgent(BaseAgent):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def handle(self, payload: dict) -> dict:
        doc_types = payload.get("doc_types", [])
        documents = [
            {"type": doc_type, "content": self.llm_service.generate(f"Generate {doc_type}")} for doc_type in doc_types
        ]
        return {"documents": documents}
