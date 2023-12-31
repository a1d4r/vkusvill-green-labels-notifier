from vkusvill_green_labels.services.vkusvill import GreenLabelItem, VkusvillApi
from vkusvill_green_labels.storage import GreenLabelsStorage


class GreenLabelsUpdater:
    def __init__(
        self,
        vkusvill_api: VkusvillApi,
        storage: GreenLabelsStorage,
        shop_id: int,
    ) -> None:
        self.api = vkusvill_api
        self.items_storage = storage
        self.shop_id = shop_id

    def update(self) -> list[GreenLabelItem]:
        """Update green labels from vkusvill API and return newly appeared items."""
        items = self.api.fetch_green_labels(self.shop_id)
        new_items = self._get_items_difference(items, self.items_storage.get_items())
        self.items_storage.set_items(items)
        return list(new_items)

    @staticmethod
    def _get_items_difference(
        new_items: list[GreenLabelItem],
        old_items: list[GreenLabelItem],
    ) -> list[GreenLabelItem]:
        """Return green label items which only appears in `new_items` list."""
        old_item_ids = {item.item_id for item in old_items}
        return [item for item in new_items if item.item_id not in old_item_ids]
