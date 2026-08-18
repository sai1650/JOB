from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "candidate-screening-ai"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Database
    DATABASE_URL: str
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "candidate_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # CORS
    CORS_ALLOW_ORIGINS: str = "*"
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 300
    RATE_LIMIT_WINDOW: int = 60
    # LLM retry settings
    LLM_RETRY_COUNT: int = 3

    # Authentication - JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Default credentials
    ADMIN_EMAIL: str = "admin@screening-ai.com"
    ADMIN_PASSWORD: str = "Admin123!@#"
    ADMIN_NAME: str = "System Administrator"
    TEST_USER_EMAIL: str = "test@screening-ai.com"
    TEST_USER_PASSWORD: str = "Test123!@#"
    TEST_USER_NAME: str = "Test User"

    model_config = {
        "env_file": "../.env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
