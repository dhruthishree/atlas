from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ATLAS Enterprise Decision Intelligence"
    PORT: int = 8002
    HOST: str = "0.0.0.0"
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    GENERATION_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "text-embedding-004"

    # Core Engine (Rust Axum Service)
    RUST_CORE_URL: str = "http://localhost:8080"

    # Qdrant Vector DB
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "atlas_enterprise_knowledge"

    # Pricing per 1M tokens (Gemini 2.5 Flash)
    COST_PER_1M_INPUT_TOKENS: float = 0.075
    COST_PER_1M_OUTPUT_TOKENS: float = 0.30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
