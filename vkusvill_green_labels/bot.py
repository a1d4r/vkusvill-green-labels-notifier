import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dishka.integrations.aiogram import setup_dishka

from vkusvill_green_labels.core.settings import settings
from vkusvill_green_labels.dependencies import container
from vkusvill_green_labels.handlers import command_router, location_router

dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(command_router, location_router)


async def main() -> None:
    setup_dishka(container=container, router=dp, auto_inject=True)
    bot = Bot(
        token=settings.telegram.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
