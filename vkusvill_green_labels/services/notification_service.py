from typing import ClassVar

from dataclasses import dataclass
from itertools import batched

from aiogram import Bot
from aiogram.utils import formatting as fmt

from vkusvill_green_labels.models.db import User
from vkusvill_green_labels.models.vkusvill import GreenLabelItem


@dataclass
class NotificationService:
    bot: Bot
    _batch_size: ClassVar[int] = 20

    async def notify_about_new_green_labels(self, user: User, items: list[GreenLabelItem]) -> None:
        for items_batch in batched(items, self._batch_size):
            text_items: list[fmt.Text] = []

            for item in items_batch:
                lines = fmt.as_line(
                    fmt.as_line(fmt.Text(fmt.Bold(item.title), " ", str(item.rating), "★")),
                    fmt.as_line(
                        fmt.Text(
                            "Цена: ",
                            fmt.Strikethrough(str(item.price)),
                            " ",
                            fmt.Italic(str(item.discount_price)),
                        )
                    ),
                    fmt.as_line(fmt.Text("Доступно: ", str(item.amount))),
                    "",
                )
                text_items.extend(lines)

            text = fmt.as_line(*text_items)

            await self.bot.send_message(user.tg_id, text.as_html())
