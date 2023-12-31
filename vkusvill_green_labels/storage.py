import abc

from vkusvill_green_labels.services import vkusvill


class GreenLabelsStorage(abc.ABC):
    @abc.abstractmethod
    def get_items(self) -> list[vkusvill.GreenLabelItem]:
        ...

    @abc.abstractmethod
    def set_items(self, items: list[vkusvill.GreenLabelItem]) -> None:
        ...


class InMemoryGreenLabelsStorage(GreenLabelsStorage):
    def __init__(self) -> None:
        self.items: list[vkusvill.GreenLabelItem] = []

    def get_items(self) -> list[vkusvill.GreenLabelItem]:
        return self.items

    def set_items(self, items: list[vkusvill.GreenLabelItem]) -> None:
        self.items = items
