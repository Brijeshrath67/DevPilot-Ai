from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DevPilot AI"
    app_version: str = "1.0.0"

    # Primary datastore. When MONGODB_URI is configured the application runs
    # against MongoDB Atlas; otherwise it gracefully falls back to SQLite.
    database_url: str = "sqlite:///./devpilot.db"
    mongodb_uri: str = ""
    mongodb_db_name: str = "devpilot_ai"

    # Default development-only secret; always override via JWT_SECRET_KEY in production.
    jwt_secret_key: str = "devpilot_secret_key_12345"  # noqa: S105
    github_client_id: str | None = None
    github_client_secret: str | None = None

    ai_api_key: str = "mock_key"
    ai_api_url: str = "https://api.openai.com/v1"

    # ---- Multi-provider LLM routing -----------------------------------------
    # Each specialized agent is backed by a distinct LLM provider. Keys are
    # optional: when a provider key is missing, the generic AI_API_KEY is used,
    # so the app keeps working offline with a single mock key.
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"

    mistral_api_key: str = ""
    mistral_base_url: str = "https://api.mistral.ai/v1"
    mistral_model: str = "mistral-large-latest"

    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "meta/llama-3.3-70b-instruct"

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"

    cerebras_api_key: str = ""
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    cerebras_model: str = "gpt-oss-120b"

    huggingface_api_key: str = ""
    huggingface_base_url: str = "https://router.huggingface.co/v1"
    huggingface_model: str = "meta-llama/Llama-3.3-70B-Instruct"

    # Maps each agent to the provider it should use.
    agent_llm_providers: dict[str, str] = {
        "repository_analyzer": "groq",
        "code_review": "huggingface",
        "documentation": "mistral",
        "testing": "nvidia",
        "repository_chat": "openrouter",
        "project_health": "cerebras",
    }

    cors_origins: list[str] = ["*"]
    data_root: str = "./data"

    # Vector store. Set VECTOR_STORE=pinecone and provide PINECONE_API_KEY to
    # use Pinecone; otherwise a local JSON-backed index is used.
    vector_store: str = "local"  # "pinecone" | "local"
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "devpilot-vectors"

    log_level: str = "INFO"

    @property
    def use_mongodb(self) -> bool:
        return bool(self.mongodb_uri)

    @property
    def use_pinecone(self) -> bool:
        return bool(self.pinecone_api_key) and self.vector_store.lower() == "pinecone"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
