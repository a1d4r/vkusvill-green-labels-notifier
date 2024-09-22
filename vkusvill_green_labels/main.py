import asyncio

from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka.integrations.aiogram import setup_dishka
from loguru import logger

from vkusvill_green_labels.bot import bot, dp
from vkusvill_green_labels.core.settings import settings
from vkusvill_green_labels.dependencies import container
from vkusvill_green_labels.jobs import check_green_labels


async def main() -> None:
    logger.info("Starting application")
    scheduler = AsyncIOScheduler()
    setup_dishka(container=container, router=dp, auto_inject=True)
    scheduler.add_job(
        check_green_labels,
        trigger="interval",
        seconds=settings.update_interval,
        next_run_time=datetime.now(UTC),
    )
    logger.info("Starting scheduler")
    scheduler.start()
    logger.info("Starting polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())