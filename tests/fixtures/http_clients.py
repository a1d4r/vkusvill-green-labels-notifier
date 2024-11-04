from collections.abc import AsyncIterator

import httpx
import pytest

from vkusvill_green_labels.core.settings import VkusvillSettings
from vkusvill_green_labels.models.vkusvill import VkusvillUserSettings
from vkusvill_green_labels.services.vkusvill_api import VkusvillApi


@pytest.fixture
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
def vkusvill_api(
    vkusvill_settings: VkusvillSettings, http_client: httpx.AsyncClient
) -> VkusvillApi:
    return VkusvillApi(http_client, vkusvill_settings)


@pytest.fixture
def authorized_vkusvill_api(
    vkusvill_settings: VkusvillSettings, http_client: httpx.AsyncClient
) -> VkusvillApi:
    user_settings = VkusvillUserSettings(device_id="test", user_number="test", token="test")
    return VkusvillApi(http_client, vkusvill_settings, user_settings)
