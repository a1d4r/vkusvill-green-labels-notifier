import sys

from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, PositiveInt, SecretStr
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


class VkusvillSettings(BaseModel):
    green_labels: EndpointSettings
    create_token: EndpointSettings
    shop_info: EndpointSettings
    address_info: EndpointSettings
    update_cart: EndpointSettings


class TelegramSettings(BaseModel):
    bot_token: SecretStr = Field(..., description="Token from @BotFather")
    user_id: int = Field(..., description="ID of the user to send updates")


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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    vkusvill: VkusvillSettings
    telegram: TelegramSettings
    database: DatabaseSettings
    address_latitude: Decimal
    address_longitude: Decimal
    update_interval: int = Field(..., description="Update interval in seconds")


env_file = PROJECT_ROOT / ".env"
if "pytest" in sys.modules:
    env_file = PROJECT_ROOT / ".env.test"

settings = Settings(vkusvill=load_vkusvill_settings(), _env_file=env_file)