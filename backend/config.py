import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """System-wide configuration settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://isro_admin:CloudFreeAI_Secure_Password_2026@db:5432/cloudfree_gis",
        validation_alias="DATABASE_URL"
    )
    
    # Redis for task queuing
    REDIS_URL: str = Field(
        default="redis://redis:6379/0",
        validation_alias="REDIS_URL"
    )
    
    # Gemini API Key
    GEMINI_API_KEY: str = Field(
        default="YOUR_GEMINI_API_KEY",
        validation_alias="GEMINI_API_KEY"
    )
    
    # JWT Security Configuration
    SECRET_KEY: str = Field(
        default="ISRO_NRSC_SECRET_TOKEN_COMPACT_KEY_2026_BAH",
        validation_alias="JWT_SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours

    class Config:
        env_file = ".env"
        extra = "ignore"

# Global settings instance
settings = Settings()
