import json
import pathlib

import pytest

from vkusvill_green_labels.settings import Settings, settings


@pytest.fixture()
def app_settings() -> Settings:
    return settings


@pytest.fixture()
def static_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "static"


@pytest.fixture()
def load_json(static_path):
    def _load_json(filename: str):
        with (static_path / filename).open("r") as file:
            return json.load(file)

    return _load_json
