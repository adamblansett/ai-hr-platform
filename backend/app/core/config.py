from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "ai-hr-platform"
    ENVIRONMENT: str = "development"  # development | staging | production
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "replace-this-in-production-with-a-secure-random-32-byte-hex-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    ALGORITHM: str = "HS256"

    # Multi-tenant and CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    ENABLE_SECURITY_HEADERS: bool = True

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ai_hr_db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key_production(cls, v: str, info) -> str:
        env = info.data.get("ENVIRONMENT", "development")
        if env == "production" and ("replace-this" in v or len(v) < 32):
            raise ValueError("Insecure default SECRET_KEY detected in production environment! Must be 32+ char random key.")
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str) and v:
            return v
        data = info.data
        server = data.get("POSTGRES_SERVER", "localhost")
        user = data.get("POSTGRES_USER", "postgres")
        password = data.get("POSTGRES_PASSWORD", "postgres")
        port = data.get("POSTGRES_PORT", 5432)
        db = data.get("POSTGRES_DB", "ai_hr_db")
        return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"

    # Celery & Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Provider Settings
    PRIMARY_LLM_PROVIDER: str = "ollama" # ollama | openai | anthropic
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b" # options: llama3.1:8b, qwen2.5:7b, mistral-nemo:12b
    EMBEDDING_MODEL: str = "nomic-embed-text"
    FALLBACK_OPENAI_API_KEY: Optional[str] = None
    FALLBACK_ANTHROPIC_API_KEY: Optional[str] = None

    # Upstream Integrations
    RECRUITER_WEBHOOK_SECRET: str = "dev-shared-recruiter-webhook-secret-key"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
