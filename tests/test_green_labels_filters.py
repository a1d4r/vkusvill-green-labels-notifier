import pytest

from vkusvill_green_labels.models.filter_operators import (
    AndOperator,
    TitleBlackListOperator,
    TitleWhiteListOperator,
)
from vkusvill_green_labels.models.vkusvill import GreenLabelItem
from vkusvill_green_labels.services.vkusvill_api import GreenLabelItemResponse


@pytest.fixture
def green_labels_items(load_json) -> list[GreenLabelItem]:
    return [
        GreenLabelItem.model_validate(GreenLabelItemResponse.model_validate(item))
        for item in load_json("green_labels_2.json")
    ]


def test_title_whitelist_filter(green_labels_items: list[GreenLabelItem]):
    # Arrange
    filter_operator = TitleWhiteListOperator(whitelist=["лук", "капуста"])

    # Act
    filtered_items_titles = [
        green_label_item.title
        for green_label_item in green_labels_items
        if filter_operator.satisfies(green_label_item)
    ]

    # Assert
    assert filtered_items_titles == ["Капуста белокочанная", "Лук репчатый"]


def test_title_blacklist_filter(green_labels_items: list[GreenLabelItem]):
    # Arrange
    filter_operator = TitleBlackListOperator(blacklist=["хлеб", "блин", "х/б"])

    # Act
    filtered_items_titles = [
        green_label_item.title
        for green_label_item in green_labels_items
        if filter_operator.satisfies(green_label_item)
    ]

    # Assert
    assert filtered_items_titles == [
        "Капуста белокочанная",
        "Лук репчатый",
        "Камбала стейк вяленый, 100 г",
        "Ряпушка вяленая, 200 г",
    ]


def test_and_operator(green_labels_items: list[GreenLabelItem]):
    # Arrange
    filter_operator = AndOperator(
        operands=[
            TitleWhiteListOperator(whitelist=["лук", "капуста"]),
            TitleBlackListOperator(blacklist=["репчатый"]),
        ]
    )

    # Act
    filtered_items_titles = [
        green_label_item.title
        for green_label_item in green_labels_items
        if filter_operator.satisfies(green_label_item)
    ]

    # Assert
    assert filtered_items_titles == ["Капуста белокочанная"]
