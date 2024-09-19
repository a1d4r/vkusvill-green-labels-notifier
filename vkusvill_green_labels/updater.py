from vkusvill_green_labels.repositories.green_labels import GreenLabelsRepository
from vkusvill_green_labels.services.vkusvill import GreenLabelItem, VkusvillApi


class GreenLabelsUpdater:
    def __init__(self, vkusvill_api: VkusvillApi, green_labels_repo: GreenLabelsRepository) -> None:
        self.api = vkusvill_api
        self.green_labels_repo = green_labels_repo

    def update(self) -> list[GreenLabelItem]:
        """Update green labels from vkusvill API and return newly appeared items."""
        items = self.api.fetch_green_labels()
        new_items = self._get_items_difference(items, self.green_labels_repo.get_items())
        self.green_labels_repo.set_items(items)
        return list(new_items)

    @staticmethod
    def _get_items_difference(
        new_items: list[GreenLabelItem], old_items: list[GreenLabelItem]
    ) -> list[GreenLabelItem]:
        """Return green label items which only appears in `new_items` list."""
        old_item_ids = {item.item_id for item in old_items}
        return [item for item in new_items if item.item_id not in old_item_ids]
