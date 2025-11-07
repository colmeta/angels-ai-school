from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field, HttpUrl, validator


class Settings(BaseSettings):
    """Global application configuration loaded from environment variables."""

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # Clarity Engine
    clarity_api_key: Optional[str] = Field(default=None, env="CLARITY_API_KEY")
    clarity_base_url: HttpUrl = Field(
        default="https://veritas-engine-zae0.onrender.com", env="CLARITY_BASE_URL"
    )

    # Optional fallback LLM providers
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")

    # Branding defaults (per school overrides stored in DB)
    default_brand_name: str = Field(default="Angels AI School", env="DEFAULT_BRAND_NAME")
    default_brand_primary_color: str = Field(
        default="#0B69FF", env="DEFAULT_BRAND_PRIMARY_COLOR"
    )
    default_brand_accent_color: str = Field(
        default="#FFB400", env="DEFAULT_BRAND_ACCENT_COLOR"
    )
    default_brand_logo_url: Optional[HttpUrl] = Field(
        default=None, env="DEFAULT_BRAND_LOGO_URL"
    )

    # Feature flags
    enable_background_sync: bool = Field(default=True, env="ENABLE_BACKGROUND_SYNC")
    enable_parent_chatbot: bool = Field(default=True, env="ENABLE_PARENT_CHATBOT")

    # Whitelabel options
    allowed_brand_domains: List[str] = Field(default_factory=list, env="ALLOWED_BRAND_DOMAINS")

    # Mobile money providers (optional live credentials)
    mtn_mobile_money_api_key: Optional[str] = Field(default=None, env="MTN_MOBILE_MONEY_API_KEY")
    mtn_mobile_money_base_url: Optional[HttpUrl] = Field(
        default="https://api.mtn.com/mobilemoney", env="MTN_MOBILE_MONEY_BASE_URL"
    )
    airtel_mobile_money_api_key: Optional[str] = Field(
        default=None, env="AIRTEL_MOBILE_MONEY_API_KEY"
    )
    airtel_mobile_money_base_url: Optional[HttpUrl] = Field(
        default="https://openapi.airtel.africa/mobile-money", env="AIRTEL_MOBILE_MONEY_BASE_URL"
    )

    # Chatbot integration (optional external provider)
    chatbot_api_key: Optional[str] = Field(default=None, env="CHATBOT_API_KEY")
    chatbot_api_base_url: Optional[HttpUrl] = Field(default=None, env="CHATBOT_API_BASE_URL")

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("allowed_brand_domains", pre=True)
    def split_allowed_domains(cls, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
