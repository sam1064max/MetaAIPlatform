from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "MetaAI Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/metaai"
    REDIS_URL: str = "redis://redis:6379/0"
    QDRANT_URL: str = "http://qdrant:6333"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_SECRET: str = "jwt-secret-change-in-production"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "metaai"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
