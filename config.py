"""
Configuration management using pydantic-settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Twilio Configuration
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str

    # Application Configuration
    app_name: str = "Twilio WhatsApp Bot"
    app_env: Literal["development", "production"] = "development"
    log_level: str = "INFO"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
