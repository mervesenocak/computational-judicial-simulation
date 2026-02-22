from pydantic_settings import BaseSettings, SettingsConfigDict

class Ayarlar(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "dev"
    SQLITE_URL: str = "sqlite:///./hakim.db"

    # OpenAI opsiyonel (şimdilik kapalı)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_ENABLED: bool = False

ayarlar = Ayarlar()