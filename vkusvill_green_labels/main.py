import asyncio

from datetime import UTC, datetime, timedelta

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka.integrations.aiogram import setup_dishka

from vkusvill_green_labels.bot import bot, dp
from vkusvill_green_labels.core.settings import settings
from vkusvill_green_labels.core.setup_logging import setup_logging
from vkusvill_green_labels.core.setup_sentry import setup_sentry
from vkusvill_green_labels.dependencies import container
from vkusvill_green_labels.jobs import check_green_labels
from vkusvill_green_labels.routes.health import health


async def main() -> None:
    # Настроить логи и отправку ошибок в Sentry
    setup_logging()
    setup_sentry()

    # Настроить интеграцию DI фреймворка с aiogram
    setup_dishka(container=container, router=dp, auto_inject=True)

    # Запустить планировщик и фоновые задачи
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_green_labels,
        trigger="interval",
        seconds=settings.update_interval,
        next_run_time=datetime.now(UTC) + timedelta(seconds=1),
    )
    scheduler.start()

    # Настроить и запустить веб-сервер
    app = web.Application()
    app.add_routes([web.get("/health", health)])
    if settings.telegram.webhook_settings_provided:
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=settings.telegram.webhook_secret.get_secret_value(),  # type: ignore[union-attr]
        )
        webhook_requests_handler.register(app, path=settings.telegram.webhook_path)  # type: ignore[arg-type]
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.web_server.host, settings.web_server.port)
    await site.start()

    # Запустить поллинг, если не задан вебхук
    if not settings.telegram.webhook_settings_provided:
        await bot.delete_webhook()
        await dp.start_polling(bot)
    else:
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
