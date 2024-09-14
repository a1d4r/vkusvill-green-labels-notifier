import pytest

from requests_mock import Mocker

from vkusvill_green_labels.services.vkusvill import VkusvillApi
from vkusvill_green_labels.storage import InMemoryGreenLabelsStorage
from vkusvill_green_labels.updater import GreenLabelsUpdater


@pytest.fixture
def _mock_vkusvill_api(requests_mock: Mocker, load_json, app_settings):
    base_response = load_json("green_labels_response.json")

    responses = [{"status": "success"} for _ in range(4)]
    responses[0]["payload"] = base_response["payload"][:3]
    responses[1]["payload"] = base_response["payload"][1:5]
    responses[2]["payload"] = base_response["payload"][3:8]
    responses[3]["payload"] = base_response["payload"][5:6]

    requests_mock.get(
        str(app_settings.vkusvill.green_labels_endpoint),
        response_list=[{"json": response, "status_code": 200} for response in responses],
    )


@pytest.mark.usefixtures("_mock_vkusvill_api")
def test_updater(app_settings):
    updater = GreenLabelsUpdater(
        vkusvill_api=VkusvillApi(app_settings.vkusvill),
        storage=InMemoryGreenLabelsStorage(),
        shop_id=5266,
    )

    updater.update()
    new_items1 = updater.update()
    new_items2 = updater.update()
    new_items3 = updater.update()

    assert [item.item_id for item in new_items1] == [72682, 72191]
    assert [item.item_id for item in new_items2] == [61689, 43242, 36843]
    assert new_items3 == []
