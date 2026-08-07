from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService

class CodeReviewAgent(BaseAgent):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def handle(self, payload: dict) -> dict:
        review_scope = payload.get("review_scope", "full")
        issues = self.llm_service.generate(f"Review code with scope {review_scope}")
        return {"issues": [], "recommendations": []}
