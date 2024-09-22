from collections.abc import AsyncIterable

import httpx

from dishka import Provider, Scope, make_async_container

from vkusvill_green_labels.core.settings import settings
from vkusvill_green_labels.services.vkusvill_api import VkusvillApi


async def provide_httpx_client() -> AsyncIterable[httpx.AsyncClient]:
    async with httpx.AsyncClient() as client:
        yield client


async def provide_vkusvill_api(client: httpx.AsyncClient) -> VkusvillApi:
    return VkusvillApi(client, settings.vkusvill)


provider = Provider()
provider.provide(provide_httpx_client, scope=Scope.REQUEST)
provider.provide(provide_vkusvill_api, scope=Scope.REQUEST)

container = make_async_container(provider)
