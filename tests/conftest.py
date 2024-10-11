import json
import pathlib

import pytest

from vkusvill_green_labels.core.settings import VkusvillSettings, settings

pytest_plugins = [
    "tests.fixtures.containers",
    "tests.fixtures.db",
    "tests.fixtures.http_clients",
    "tests.fixtures.repositories",
    "tests.fixtures.services",
]


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
