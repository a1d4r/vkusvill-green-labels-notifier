from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from vkusvill_green_labels.core.middleware.sentry import AiogramSentryContextMiddleware
from vkusvill_green_labels.core.settings import settings
from vkusvill_green_labels.handlers import (
    command_router,
    filter_router,
    location_router,
    menu_router,
    notifications_router,
)


async def on_startup(bot: Bot) -> None:
    if settings.telegram.webhook_settings_provided:
        await bot.set_webhook(
            settings.telegram.webhook_full_path,  # type: ignore[arg-type]
            secret_token=settings.telegram.webhook_secret.get_secret_value(),  # type: ignore[union-attr]
        )


dp = Dispatcher(storage=RedisStorage.from_url(str(settings.redis.dsn)))
dp.startup.register(on_startup)
dp.include_routers(
    command_router, menu_router, location_router, notifications_router, filter_router
)
dp.message.middleware(AiogramSentryContextMiddleware())

bot = Bot(
    token=settings.telegram.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
