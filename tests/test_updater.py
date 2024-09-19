import pytest

from requests_mock import Mocker

from vkusvill_green_labels.services.vkusvill import VkusvillApi
from vkusvill_green_labels.settings import VkusvillSettings
from vkusvill_green_labels.storage import InMemoryGreenLabelsStorage
from vkusvill_green_labels.updater import GreenLabelsUpdater


@pytest.fixture
def _mock_vkusvill_api(requests_mock: Mocker, load_json, vkusvill_settings: VkusvillSettings):
    green_label_items = load_json("green_labels.json")

    responses = [
        green_label_items[:3],
        green_label_items[1:5],
        green_label_items[3:8],
        green_label_items[5:6],
    ]

    requests_mock.get(
        str(vkusvill_settings.green_labels.url),
        response_list=[{"json": response, "status_code": 200} for response in responses],
    )


@pytest.mark.usefixtures("_mock_vkusvill_api")
def test_updater(authorized_vkusvill_api: VkusvillApi):
    updater = GreenLabelsUpdater(
        vkusvill_api=authorized_vkusvill_api, storage=InMemoryGreenLabelsStorage()
    )

    updater.update()
    new_items1 = updater.update()
    new_items2 = updater.update()
    new_items3 = updater.update()

    assert [item.item_id for item in new_items1] == [78244, 69495]
    assert [item.item_id for item in new_items2] == [19081, 34217, 14739]
    assert new_items3 == []
