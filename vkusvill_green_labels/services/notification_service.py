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
        """Отправить уведомления о новых товарах с зелёными ценниками."""
        for items_batch in batched(items, self._batch_size):
            text_items: list[fmt.Text] = []

            for item in items_batch:
                text_items.extend(self._format_item_text(item))

            text = fmt.as_line(*text_items)

            await self.bot.send_message(user.tg_id, text.as_html())

    @staticmethod
    def _format_item_text(item: GreenLabelItem) -> fmt.Text:
        """Сформировать текст уведомления."""
        item_line_elements: list[fmt.Text | list[fmt.Text]] = []

        # Собираем заголовок (Наименование товара и оценка)
        title_line_items: list[fmt.Text | str] = [fmt.Bold(item.title_display_string)]
        if len(item.rating) < 4:
            # Не выводить "Я новенький" и "Ждёт оценку", добавлять только оценки вида 4.5
            title_line_items.extend([" ", str(item.rating), "★"])
        title_line = fmt.as_line(*title_line_items)
        item_line_elements.append(title_line)

        # Добавляем информацию о весе
        if item.weight_str:
            weight_line = fmt.as_line("Вес: ", fmt.Italic(item.weight_str))
            item_line_elements.append(weight_line)

        # Собираем информацию о цене
        price_line = fmt.as_line(
            fmt.Text(
                "Цена: ",
                fmt.Strikethrough(str(item.price)),
                " ",
                fmt.Italic(f"{item.discount_price}₽/{item.weight_unit}"),
            )
        )
        item_line_elements.append(price_line)

        # Собираем информацию о доступности (остатки товара)
        available_line = fmt.as_line(fmt.Text("Доступно: ", str(item.available_display_string)))
        item_line_elements.append(available_line)

        return fmt.as_line(*item_line_elements)
