import datetime
import decimal
import zoneinfo

import pytest
from requests_mock import Mocker

from vkusvill_green_labels.services.vkusvill import VkusvillApi


@pytest.fixture()
def _mock_vkusvill_api(requests_mock: Mocker, load_json):
    response = load_json("green_labels_response.json")
    requests_mock.get("https://mobile.vkusvill.ru/api/takeaway/getGreenLabelsShop", json=response)


@pytest.mark.usefixtures("_mock_vkusvill_api")
def test_fetch_green_labels(app_settings):
    vkusvill_api = VkusvillApi(app_settings.vkusvill)

    green_labels_items = vkusvill_api.fetch_green_labels(5266)

    assert len(green_labels_items) == 56
    assert green_labels_items[0].shop_id == 5266
    assert green_labels_items[0].item_id == 70127
    assert green_labels_items[0].name == "Азу по-татарски с картофельным пюре"  # noqa: RUF001
    assert green_labels_items[0].rating == "4.8"
    assert (
        str(green_labels_items[0].photo_url)
        == "https://img.vkusvill.ru/pim/images/m_thumb/dde28adb-e96b-494a-b23a-64590f55234f.jpg?1674590621.2754"
    )
    assert green_labels_items[0].timestamp == datetime.datetime(
        2023, 9, 13, 10, 8, 0, 47000, tzinfo=zoneinfo.ZoneInfo("Europe/Moscow")
    )
    assert green_labels_items[0].unit_of_measurement == "шт"
    assert green_labels_items[0].weight == decimal.Decimal("0.23")
    assert green_labels_items[0].discount_percents == decimal.Decimal("40")
    assert green_labels_items[0].units_available == decimal.Decimal("5")
    assert green_labels_items[0].price == decimal.Decimal("248")
    assert green_labels_items[0].price_discount == decimal.Decimal("149")
