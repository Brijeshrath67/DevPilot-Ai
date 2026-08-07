from typing import Any
from app.services.llm_service import LLMService

class LLMSkill:
    def __init__(self, api_key: str, api_url: str):
        self.llm_service = LLMService(api_key, api_url)

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        return self.llm_service.generate(prompt, temperature=temperature, max_tokens=max_tokens)
