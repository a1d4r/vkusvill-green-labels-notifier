import simplejson

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from vkusvill_green_labels.core.settings import settings
from vkusvill_green_labels.handlers import command_router, location_router

dp = Dispatcher(
    storage=RedisStorage.from_url(
        str(settings.redis.dsn), json_loads=simplejson.loads, json_dumps=simplejson.dumps
    )
)
dp.include_routers(command_router, location_router)

bot = Bot(
    token=settings.telegram.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
