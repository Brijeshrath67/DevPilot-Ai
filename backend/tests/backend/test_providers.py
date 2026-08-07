"""Unit tests for the multi-provider LLM routing layer."""

from app.core.config import Settings
from app.core.providers import DEFAULT_BASE_URLS, DEFAULT_MODELS, LLMProviderRegistry


class TestLLMProviderRegistry:
    def test_all_providers_resolve(self):
        registry = LLMProviderRegistry(Settings())
        providers = ["groq", "mistral", "nvidia", "openrouter", "cerebras", "huggingface"]
        services = {name: registry.get_service(name) for name in providers}

        for name in providers:
            service = services[name]
            assert service.provider == name
            assert service.model
            assert service.api_url == DEFAULT_BASE_URLS[name]

    def test_default_models_match_documented_providers(self):
        assert len(DEFAULT_MODELS) == 6
        assert len(DEFAULT_BASE_URLS) == 6
        assert set(DEFAULT_MODELS) == set(DEFAULT_BASE_URLS)

    def test_every_agent_has_a_distinct_provider(self):
        settings = Settings()
        mapping = settings.agent_llm_providers
        assert len(mapping) == 6
        assert len(set(mapping.values())) == 6
        assert set(mapping.values()) <= set(DEFAULT_MODELS)

    def test_service_for_agent_routes_to_provider(self):
        settings = Settings()
        registry = LLMProviderRegistry(settings)
        service = registry.service_for_agent("documentation")
        assert service.provider == settings.agent_llm_providers["documentation"]

    def test_provider_api_key_falls_back_to_generic_key(self):
        settings = Settings(ai_api_key="generic_key")
        registry = LLMProviderRegistry(settings)
        service = registry.get_service("groq")
        assert service.api_key == "generic_key"

    def test_provider_specific_key_overrides_generic(self):
        settings = Settings(ai_api_key="generic_key", groq_api_key="groq_specific")
        registry = LLMProviderRegistry(settings)
        service = registry.get_service("groq")
        assert service.api_key == "groq_specific"

    def test_unknown_agent_falls_back_to_openrouter(self):
        registry = LLMProviderRegistry(Settings())
        assert registry.service_for_agent("does_not_exist").provider == "openrouter"

    def test_llm_service_holds_provider_provenance(self):
        from app.services.llm_service import LLMService

        service = LLMService(api_key="k", api_url="https://x/v1", model="m", provider="groq")
        assert service.provider == "groq"
