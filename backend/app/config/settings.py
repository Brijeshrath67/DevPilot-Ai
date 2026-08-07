from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl

class Settings(BaseSettings):
    app_name: str = "DevPilot AI"
    database_url: str = "sqlite:///./devpilot.db"
    jwt_secret_key: str = "devpilot_secret_key_12345"
    github_client_id: str | None = None
    github_client_secret: str | None = None
    ai_api_key: str = "mock_key"
    ai_api_url: str = "https://api.openai.com/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
