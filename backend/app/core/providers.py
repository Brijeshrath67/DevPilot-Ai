"""Multi-provider LLM routing.

Each specialized agent is backed by a distinct LLM provider. All six providers
(Groq, Gemini, Mistral, NVIDIA, OpenRouter, Cerebras) expose an
OpenAI-compatible chat completions endpoint, so ``LLMService`` can drive them
all. This module builds a per-provider ``LLMService`` from settings and resolves
the provider assigned to each agent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.core.logger import get_logger
from app.services.llm_service import LLMService

if TYPE_CHECKING:
    from app.core.config import Settings

logger = get_logger(__name__)

DEFAULT_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.0-flash",
    "mistral": "mistral-large-latest",
    "nvidia": "meta/llama-3.3-70b-instruct",
    "openrouter": "openai/gpt-4o-mini",
    "cerebras": "llama3.1-8b",
}

DEFAULT_BASE_URLS = {
    "groq": "https://api.groq.com/openai/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "mistral": "https://api.mistral.ai/v1",
    "nvidia": "https://integrate.api.nvidia.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "cerebras": "https://api.cerebras.ai/v1",
}


@dataclass(frozen=True)
class LLMProvider:
    """One routed LLM provider for an agent."""

    name: str
    api_key: str
    base_url: str
    model: str


class LLMProviderRegistry:
    """Resolves per-agent provider services from the active settings."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_service(self, provider: str) -> LLMService:
        config = self._provider_config(provider)
        return LLMService(
            api_key=config.api_key,
            api_url=config.base_url,
            model=config.model,
            provider=config.name,
        )

    def service_for_agent(self, agent_name: str) -> LLMService:
        provider = self.settings.agent_llm_providers.get(agent_name, "openrouter")
        service = self.get_service(provider)
        logger.debug("Agent '%s' routed to LLM provider '%s'", agent_name, provider)
        return service

    def _provider_config(self, provider: str) -> LLMProvider:
        key = self._env_key(provider)
        api_key = getattr(self.settings, key) or self.settings.ai_api_key
        base_url = getattr(self.settings, f"{provider}_base_url", "") or DEFAULT_BASE_URLS.get(
            provider, self.settings.ai_api_url
        )
        model = getattr(self.settings, f"{provider}_model", "") or DEFAULT_MODELS.get(provider, "gpt-4o-mini")
        return LLMProvider(name=provider, api_key=api_key, base_url=base_url, model=model)

    @staticmethod
    def _env_key(provider: str) -> str:
        return f"{provider}_api_key"
