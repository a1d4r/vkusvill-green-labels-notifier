from datetime import UTC, datetime

import telebot
import telebot.formatting as fmt

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from vkusvill_green_labels.services.vkusvill import VkusvillApi
from vkusvill_green_labels.settings import settings
from vkusvill_green_labels.storage import InMemoryGreenLabelsStorage
from vkusvill_green_labels.updater import GreenLabelsUpdater

updater = GreenLabelsUpdater(
    vkusvill_api=VkusvillApi(settings.vkusvill), storage=InMemoryGreenLabelsStorage()
)
scheduler = BackgroundScheduler()
bot = telebot.TeleBot(settings.telegram.bot_token.get_secret_value())


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda _message: True)
def echo_message(message: telebot.types.Message) -> None:
    bot.reply_to(message, message.text)


def check_green_labels() -> None:
    logger.info("Checking updates for green labels...")
    new_items = updater.update()

    if not new_items:
        logger.info("No new items found :(")
        return

    logger.info("Found {} new items", len(new_items))
    logger.debug(new_items)

    text = ""
    for item in new_items:
        text += (
            fmt.mbold(fmt.escape_markdown(item.title))
            + " "
            + fmt.escape_markdown(item.rating)
            + "★\n"
            + "Цена: "
            + fmt.mstrikethrough(fmt.escape_markdown(str(item.price)))
            + " "
            + fmt.mitalic(fmt.escape_markdown(str(item.discount_price)))
            + "\n"
            + "Доступно: "
            + fmt.escape_markdown(str(int(item.amount)))
            + "\n\n"
        )

    bot.send_message(settings.telegram.user_id, text, parse_mode="MarkdownV2")


if __name__ == "__main__":
    logger.info("Starting background task...")
    scheduler.add_job(
        check_green_labels,
        trigger="interval",
        seconds=settings.update_interval,
        next_run_time=datetime.now(UTC),
    )
    scheduler.start()
    logger.info("Starting bot...")
    bot.infinity_polling()
