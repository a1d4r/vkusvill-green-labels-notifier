from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).parent.parent.parent


def load_vkusvill_settings() -> "VkusvillSettings":
    with (ROOT_DIR / "vkusvill_settings.json").open() as file:
        return VkusvillSettings.model_validate_json(file.read())


class VkusvillSettings(BaseModel):
    headers: dict[str, str]
    green_labels_endpoint: HttpUrl


class Settings(BaseSettings):
    vkusvill: VkusvillSettings = Field(default_factory=load_vkusvill_settings)


settings = Settings()
