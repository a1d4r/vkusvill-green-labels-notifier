import sys

from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, PositiveInt, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_vkusvill_settings() -> "VkusvillSettings":
    vkusvill_settings_path = Path(PROJECT_ROOT) / "vkusvill_settings.json"
    if "pytest" in sys.modules:
        vkusvill_settings_path = Path(PROJECT_ROOT) / "test_vkusvill_settings.json"
    with vkusvill_settings_path.open() as file:
        return VkusvillSettings.model_validate_json(file.read())


class EndpointSettings(BaseModel):
    headers: dict[str, str] = Field(..., description="Headers for the request")
    query: dict[str, str] = Field(..., description="Query parameters for the request")
    url: HttpUrl = Field(..., description="URL of the endpoint")
    str_params: dict[str, str] = Field({}, description="Parameters to build str_par")
    timeout: float = Field(5.0, description="Timeout, in seconds")


class VkusvillSettings(BaseModel):
    green_labels: EndpointSettings
    create_token: EndpointSettings
    shop_info: EndpointSettings
    address_info: EndpointSettings
    update_cart: EndpointSettings


class TelegramSettings(BaseModel):
    bot_token: SecretStr = Field(..., description="Token from @BotFather")
    base_webhook_url: str | None = Field(
        None, description="Base URL for webhook (public DNS with HTTPS support)"
    )
    webhook_path: str | None = Field(
        "/webhook", description="Path to webhook route, on which Telegram will send requests"
    )
    webhook_secret: SecretStr | None = Field(
        None, description="Secret key to validate requests from Telegram"
    )

    @property
    def webhook_settings_provided(self) -> bool:
        return all((self.base_webhook_url, self.webhook_path, self.webhook_secret))

    @property
    def webhook_full_path(self) -> str | None:
        if not self.base_webhook_url or not self.webhook_path:
            return None
        return f"{self.base_webhook_url}{self.webhook_path}"


class DatabaseSettings(BaseSettings):
    dialect: str = "postgresql"
    driver: str = "asyncpg"
    username: SecretStr
    password: SecretStr
    host: str
    port: int
    name: str

    pool_recycle_seconds: PositiveInt = 3600

    @property
    def url(self) -> str:
        """URL for SQLAlchemy engine.

        Format: dialect+driver://username:password@host:port/database
        More info: https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
        """
        return (
            f"{self.dialect}+{self.driver}://{self.username.get_secret_value()}:"
            f"{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"
        )


class RedisSettings(BaseSettings):
    """Настройки Redis."""

    model_config = SettingsConfigDict(extra="ignore")

    dsn: RedisDsn


class SentrySettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    dsn: str | None = None
    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0
    environment: str | None = None

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str | None) -> str | None:
        """Replace empty string with None."""
        if v is not None and not v.strip():
            return None
        return v


class WebServerSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8080


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    vkusvill: VkusvillSettings
    telegram: TelegramSettings
    database: DatabaseSettings
    redis: RedisSettings
    sentry: SentrySettings
    web_server: WebServerSettings = WebServerSettings()
    log_level: str = "INFO"
    update_interval: int = Field(..., description="Update interval in seconds")


env_file = PROJECT_ROOT / ".env"
if "pytest" in sys.modules:
    env_file = PROJECT_ROOT / ".env.test"

settings = Settings(vkusvill=load_vkusvill_settings(), _env_file=env_file)
