from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService


class TestingAgent(BaseAgent):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def handle(self, payload: dict) -> dict:
        test_types = payload.get("test_types", [])
        tests = [
            {"type": test_type, "content": self.llm_service.generate(f"Create tests for {test_type}")}
            for test_type in test_types
        ]
        return {"tests": tests}
