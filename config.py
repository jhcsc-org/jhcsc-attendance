# config.py
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from urllib.parse import quote


class Settings(BaseSettings):
    # Existing Settings
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    STUDENT_REGISTRATION_SESSION_PREFIX: str = "reg_sess"
    DATABASE_LOCAL_NAME: str = "jhcsc_local.db"

    # PostgreSQL (Supabase) Settings
    SUPABASE_USER: Optional[str] = Field(None, env="SUPABASE_USER")
    SUPABASE_PASSWORD: Optional[str] = Field(None, env="SUPABASE_PASSWORD")
    SUPABASE_HOST: Optional[str] = Field("localhost", env="SUPABASE_HOST")
    SUPABASE_PORT: Optional[int] = Field(5432, env="SUPABASE_PORT")
    SUPABASE_DB: Optional[str] = Field(None, env="SUPABASE_DB")

    # Additional Supabase Settings
    SUPABASE_PROJECT_ID: Optional[str] = Field(None, env="SUPABASE_PROJECT_ID")
    SUPABASE_URL: Optional[str] = Field(None, env="SUPABASE_URL")
    SUPABASE_PUBLIC_ANON_KEY: Optional[str] = Field(None, env="SUPABASE_PUBLIC_ANON_KEY")
    SUPABASE_SECRET_KEY: Optional[str] = Field(None, env="SUPABASE_SECRET_KEY")

    # Database URL (Optional)
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")

    # Debug Mode
    DEBUG: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instantiate settings
settings = Settings()

# URL-encode the username and password
encoded_user = quote(settings.SUPABASE_USER) if settings.SUPABASE_USER else None
encoded_password = quote(settings.SUPABASE_PASSWORD) if settings.SUPABASE_PASSWORD else None

# Construct the DATABASE_URL if not provided
if not settings.DATABASE_URL and encoded_user and encoded_password:
    settings.DATABASE_URL = (
        f"postgresql://{encoded_user}:{encoded_password}"
        f"@{settings.SUPABASE_HOST}:{settings.SUPABASE_PORT}/{settings.SUPABASE_DB}"
    )