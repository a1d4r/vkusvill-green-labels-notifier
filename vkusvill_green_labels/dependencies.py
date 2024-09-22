from collections.abc import AsyncIterable

import httpx

from dishka import Provider, Scope, make_async_container
from sqlalchemy.ext.asyncio import AsyncSession

from vkusvill_green_labels.core.database import async_session_factory
from vkusvill_green_labels.core.settings import settings
from vkusvill_green_labels.repositories.user import UserRepository
from vkusvill_green_labels.services.user_service import UserService
from vkusvill_green_labels.services.vkusvill_api import VkusvillApi
from vkusvill_green_labels.services.vkusvill_service import VkusvillService


async def provide_httpx_client() -> AsyncIterable[httpx.AsyncClient]:
    async with httpx.AsyncClient() as client:
        yield client


async def provide_session() -> AsyncIterable[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def provide_vkusvill_api(client: httpx.AsyncClient) -> VkusvillApi:
    return VkusvillApi(client, settings.vkusvill)


async def provide_vkusvill_service(vkusvill_api: VkusvillApi) -> VkusvillService:
    vkusvill_service = VkusvillService(vkusvill_api)
    await vkusvill_service.authorize_with_base_user()
    return vkusvill_service


provider = Provider()
provider.provide(provide_httpx_client, scope=Scope.REQUEST)
provider.provide(provide_vkusvill_api, scope=Scope.REQUEST)
provider.provide(provide_vkusvill_service, scope=Scope.REQUEST)
provider.provide(provide_session, scope=Scope.REQUEST)
provider.provide(UserRepository, scope=Scope.REQUEST)
provider.provide(UserService, scope=Scope.REQUEST)

container = make_async_container(provider)
