import pytest

from httpx import Response
from respx import MockRouter

from vkusvill_green_labels.repositories.green_labels import InMemoryGreenLabelsRepository
from vkusvill_green_labels.services.vkusvill import VkusvillApi
from vkusvill_green_labels.settings import VkusvillSettings
from vkusvill_green_labels.updater import GreenLabelsUpdater


@pytest.fixture
def _mock_vkusvill_api(respx_mock: MockRouter, load_json, vkusvill_settings: VkusvillSettings):
    green_label_items = load_json("green_labels.json")

    responses = [
        green_label_items[:3],
        green_label_items[1:5],
        green_label_items[3:8],
        green_label_items[5:6],
    ]

    route = respx_mock.get(str(vkusvill_settings.green_labels.url))
    route.side_effect = [Response(200, json=response) for response in responses]


@pytest.mark.usefixtures("_mock_vkusvill_api")
def test_updater(authorized_vkusvill_api: VkusvillApi):
    updater = GreenLabelsUpdater(
        vkusvill_api=authorized_vkusvill_api, green_labels_repo=InMemoryGreenLabelsRepository()
    )

    updater.update()
    new_items1 = updater.update()
    new_items2 = updater.update()
    new_items3 = updater.update()

    assert [item.item_id for item in new_items1] == [78244, 69495]
    assert [item.item_id for item in new_items2] == [19081, 34217, 14739]
    assert new_items3 == []
