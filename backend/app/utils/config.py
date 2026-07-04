import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ForgeOS Backend"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./local.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    MASTER_ENCRYPTION_KEY: str = os.getenv("MASTER_ENCRYPTION_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # OAuth Settings (placeholders)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")

    class Config:
        env_file = ".env"

settings = Settings()
