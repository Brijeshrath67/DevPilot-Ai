from typing import Any

class LLMSkill:
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1024) -> str:
        return ""
