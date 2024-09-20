import json
import pathlib

import pytest

from vkusvill_green_labels.core.settings import VkusvillSettings, settings
from vkusvill_green_labels.services.vkusvill import VkusvillApi, VkusvillUserSettings


@pytest.fixture
def vkusvill_settings() -> VkusvillSettings:
    return settings.vkusvill


@pytest.fixture
def static_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "static"


@pytest.fixture
def load_json(static_path):
    def _load_json(filename: str):
        with (static_path / filename).open("r") as file:
            return json.load(file)

    return _load_json


@pytest.fixture
def vkusvill_api(vkusvill_settings: VkusvillSettings) -> VkusvillApi:
    return VkusvillApi(vkusvill_settings)


@pytest.fixture
def authorized_vkusvill_api(vkusvill_settings: VkusvillSettings) -> VkusvillApi:
    user_settings = VkusvillUserSettings(device_id="test", user_number="test", token="test")
    return VkusvillApi(vkusvill_settings, user_settings)
