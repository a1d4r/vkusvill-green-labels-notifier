from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent.parent


def load_vkusvill_settings() -> "VkusvillSettings":
    with (ROOT_DIR / "vkusvill_settings.json").open() as file:
        return VkusvillSettings.model_validate_json(file.read())


class VkusvillSettings(BaseModel):
    headers: dict[str, str] = Field(..., description="Headers for the request")
    query: dict[str, str] = Field(..., description="Query parameters for the request")
    green_labels_endpoint: HttpUrl = Field(
        ...,
        description="URL of the endpoint for fetching green label items",
    )


class TelegramSettings(BaseModel):
    bot_token: SecretStr = Field(..., description="Token from @BotFather")
    user_id: int = Field(..., description="ID of the user to send updates")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    vkusvill: VkusvillSettings = Field(default_factory=load_vkusvill_settings)
    telegram: TelegramSettings
    update_interval: int = Field(..., description="Update interval in seconds")


settings = Settings()
