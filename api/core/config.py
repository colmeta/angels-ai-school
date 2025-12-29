from functools import lru_cache
from typing import List, Optional, Union

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application configuration loaded from environment variables."""

    # Database
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    # Environment
    environment: str = Field(default="production", validation_alias="ENVIRONMENT")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    api_secret_key: str = Field(..., validation_alias="API_SECRET_KEY")  # NO DEFAULT - MUST BE SET
    
    # JWT Authentication
    jwt_secret_key: str = Field(..., validation_alias="JWT_SECRET_KEY")  # NO DEFAULT - MUST BE SET
    access_token_expire_minutes: int = Field(default=60, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Encryption
    encryption_key: str = Field(..., validation_alias="ENCRYPTION_KEY")  # NO DEFAULT - MUST BE SET
    
    # Frontend
    frontend_url: str = Field(default="http://localhost:3000", validation_alias="FRONTEND_URL")
    
    # Redis (optional)
    redis_url: Optional[str] = Field(default=None, validation_alias="REDIS_URL")
    
    # Webhooks
    webhook_base_url: Optional[str] = Field(default=None, validation_alias="WEBHOOK_BASE_URL")

    # Clarity Engine
    clarity_api_key: Optional[str] = Field(default=None, validation_alias="CLARITY_API_KEY")
    clarity_base_url: str = Field(
        default="https://veritas-engine-zae0.onrender.com", validation_alias="CLARITY_BASE_URL"
    )
    
    # Clarity Pearl AI Chatbot
    clarity_pearl_api_key: Optional[str] = Field(default=None, validation_alias="CLARITY_PEARL_API_KEY")
    clarity_pearl_api_url: str = Field(
        default="https://clarity-pearl-ai-api.onrender.com", validation_alias="CLARITY_PEARL_API_URL"
    )

    # Optional fallback LLM providers
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, validation_alias="GEMINI_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, validation_alias="GROQ_API_KEY")

    # Branding defaults (per school overrides stored in DB)
    default_brand_name: str = Field(default="Angels AI School", validation_alias="DEFAULT_BRAND_NAME")
    default_brand_primary_color: str = Field(
        default="#0B69FF", validation_alias="DEFAULT_BRAND_PRIMARY_COLOR"
    )
    default_brand_accent_color: str = Field(
        default="#FFB400", validation_alias="DEFAULT_BRAND_ACCENT_COLOR"
    )
    default_brand_logo_url: Optional[str] = Field(
        default=None, validation_alias="DEFAULT_BRAND_LOGO_URL"
    )

    # Feature flags
    enable_background_sync: bool = Field(default=True, validation_alias="ENABLE_BACKGROUND_SYNC")
    enable_parent_chatbot: bool = Field(default=True, validation_alias="ENABLE_PARENT_CHATBOT")
    enable_whatsapp: bool = Field(default=False, validation_alias="ENABLE_WHATSAPP")
    enable_sms: bool = Field(default=True, validation_alias="ENABLE_SMS")
    enable_email: bool = Field(default=False, validation_alias="ENABLE_EMAIL")
    enable_mpesa: bool = Field(default=False, validation_alias="ENABLE_MPESA")
    enable_ai_agents: bool = Field(default=True, validation_alias="ENABLE_AI_AGENTS")
    enable_ocr: bool = Field(default=True, validation_alias="ENABLE_OCR")
    demo_mode: bool = Field(default=False, validation_alias="DEMO_MODE")

    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, validation_alias="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, validation_alias="RATE_LIMIT_PER_HOUR")

    # Whitelabel options
    allowed_brand_domains: Union[List[str], str] = Field(
        default_factory=list, validation_alias="ALLOWED_BRAND_DOMAINS"
    )

    # Mobile money providers (optional live credentials)
    mtn_mobile_money_api_key: Optional[str] = Field(default=None, validation_alias="MTN_MOBILE_MONEY_API_KEY")
    mtn_mobile_money_base_url: str = Field(
        default="https://api.mtn.com/mobilemoney", validation_alias="MTN_MOBILE_MONEY_BASE_URL"
    )
    airtel_mobile_money_api_key: Optional[str] = Field(
        default=None, validation_alias="AIRTEL_MOBILE_MONEY_API_KEY"
    )
    airtel_mobile_money_base_url: str = Field(
        default="https://openapi.airtel.africa/mobile-money", validation_alias="AIRTEL_MOBILE_MONEY_BASE_URL"
    )

    # Chatbot integration (optional external provider)
    chatbot_api_key: Optional[str] = Field(default=None, validation_alias="CHATBOT_API_KEY")
    chatbot_api_base_url: Optional[str] = Field(default=None, validation_alias="CHATBOT_API_BASE_URL")
    
    # Notifications
    africas_talking_api_key: Optional[str] = Field(default=None, validation_alias="AFRICAS_TALKING_API_KEY")
    africas_talking_username: Optional[str] = Field(default="sandbox", validation_alias="AFRICAS_TALKING_USERNAME")
    africas_talking_sender_id: Optional[str] = Field(default="AngelsAI", validation_alias="AFRICAS_TALKING_SENDER_ID")
    twilio_account_sid: Optional[str] = Field(default=None, validation_alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, validation_alias="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(default=None, validation_alias="TWILIO_PHONE_NUMBER")
    sendgrid_api_key: Optional[str] = Field(default=None, validation_alias="SENDGRID_API_KEY")
    sendgrid_from_email: Optional[str] = Field(default="noreply@angelsai.school", validation_alias="SENDGRID_FROM_EMAIL")
    
    # Web Push
    vapid_public_key: Optional[str] = Field(default=None, validation_alias="VAPID_PUBLIC_KEY")
    vapid_private_key: Optional[str] = Field(default=None, validation_alias="VAPID_PRIVATE_KEY")
    vapid_email: Optional[str] = Field(default="admin@angelsai.school", validation_alias="VAPID_EMAIL")
    
    # Google Cloud Vision OCR
    google_application_credentials: Optional[str] = Field(default=None, validation_alias="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Google OAuth2 Settings
    google_client_id: Optional[str] = Field(default=None, validation_alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, validation_alias="GOOGLE_CLIENT_SECRET")
    
    # CrewAI
    crewai_telemetry_opt_out: bool = Field(default=True, validation_alias="CREWAI_TELEMETRY_OPT_OUT")

    model_config = {
        "case_sensitive": False,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # CRITICAL: Ignore extra environment variables not defined here
    }

    @field_validator("allowed_brand_domains", mode="before")
    @classmethod
    def split_allowed_domains(cls, value):
        # Handle None or empty values
        if value is None:
            return []
        # Already a list
        if isinstance(value, list):
            return value
        # Convert to string and check if empty/whitespace
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            # Split by comma and filter out empty items
            return [item.strip() for item in value.split(",") if item.strip()]
        # Fallback for any other type
        return []


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
