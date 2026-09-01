from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/customer_support"
    TEST_DATABASE_URL: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/customer_support_test"
    )

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = ""

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    INTENT_MODEL_PATH: str = ""
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.0
    MAX_COMPLAINT_LENGTH: int = 5000
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


def get_settings() -> Settings:
    return Settings()
