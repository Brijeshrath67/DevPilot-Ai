from pydantic import BaseSettings, AnyUrl

class Settings(BaseSettings):
    app_name: str = "DevPilot AI"
    database_url: str
    jwt_secret_key: str
    github_client_id: str | None = None
    github_client_secret: str | None = None
    ai_api_key: str
    ai_api_url: str = "https://api.openai.com/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
