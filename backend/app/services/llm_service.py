import httpx

from app.core.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Client for OpenAI-compatible chat completion endpoints.

    All routed providers (Groq, Hugging Face, Mistral, NVIDIA, OpenRouter)
    expose this protocol, so a single client drives every provider.
    The ``provider`` name is kept for provenance and logging.
    """

    def __init__(self, api_key: str, api_url: str, model: str | None = None, provider: str = "openai") -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.provider = provider

    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 1024, timeout: float = 120.0) -> str:
        try:
            payload = {
                "model": self.model or "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            url = f"{self.api_url.rstrip('/')}/chat/completions"
            response = httpx.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # graceful fallback per constitution
            logger.warning("LLM request to %s failed (%s); falling back to local rules.", self.provider, exc)
            return f"LLM request failed ({exc}). Falling back to local rules."
