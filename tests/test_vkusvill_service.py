import datetime
import decimal
import zoneinfo

from decimal import Decimal

import pytest

from requests_mock import Mocker

from vkusvill_green_labels.services.vkusvill import VkusvillApi
from vkusvill_green_labels.settings import Settings


@pytest.fixture
def vkusvill_api(app_settings) -> VkusvillApi:
    return VkusvillApi(app_settings.vkusvill)


def test_fetch_green_labels(
    app_settings: Settings, vkusvill_api: VkusvillApi, requests_mock: Mocker, load_json
):
    # Arrange
    response = load_json("green_labels_response.json")
    requests_mock.get(str(app_settings.vkusvill.green_labels.url), json=response)

    # Act
    green_labels_items = vkusvill_api.fetch_green_labels(5266)

    # Assert
    assert len(green_labels_items) == 56
    assert green_labels_items[0].shop_id == 5266
    assert green_labels_items[0].item_id == 70127
    assert green_labels_items[0].name == "Азу по-татарски с картофельным пюре"
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


def test_create_token(
    app_settings: Settings, vkusvill_api: VkusvillApi, requests_mock: Mocker, load_json
):
    # Arrange
    response = load_json("token_response.json")
    requests_mock.post(str(app_settings.vkusvill.create_token.url), json=response)

    # Act
    token_data = vkusvill_api.create_token()

    # Assert
    assert token_data.token == "jwt_token"
    assert token_data.user_number == "&\\123456"


def test_get_address_info(
    app_settings: Settings, vkusvill_api: VkusvillApi, requests_mock: Mocker, load_json
):
    # Arrange
    response = load_json("address_info.json")
    requests_mock.get(str(app_settings.vkusvill.address_info.url), json=response)
    lat, lon = Decimal("55.72673"), Decimal("37.622145")

    # Act
    address_info = vkusvill_api.get_address_info(lat, lon)

    # Assert
    assert address_info is not None
    assert address_info.latitude == lat
    assert address_info.longitude == lon
    assert address_info.address == "Москва, Люсиновская улица, 6"
    assert address_info.res == 1


def test_get_address_info_not_found(
    app_settings: Settings, vkusvill_api: VkusvillApi, requests_mock: Mocker, load_json
):
    # Arrange
    response = load_json("address_info_not_found.json")
    requests_mock.get(str(app_settings.vkusvill.address_info.url), json=response)
    lat, lon = Decimal("0"), Decimal("0")

    # Act
    address_info = vkusvill_api.get_address_info(lat, lon)

    # Assert
    assert address_info is None


def test_get_shop_info(
    app_settings: Settings, vkusvill_api: VkusvillApi, requests_mock: Mocker, load_json
):
    # Arrange
    response = load_json("shop_info.json")
    requests_mock.get(str(app_settings.vkusvill.shop_info.url), json=response)
    lat, lon = Decimal("55.72673"), Decimal("37.622145")

    # Act
    shop_info = vkusvill_api.get_shop_info(lat, lon)

    # Assert
    assert shop_info is not None
    assert shop_info.shop_number == 8145


def test_get_shop_info_not_found(
    app_settings: Settings, vkusvill_api: VkusvillApi, requests_mock: Mocker, load_json
):
    # Arrange
    response = load_json("shop_info_not_found.json")
    requests_mock.get(str(app_settings.vkusvill.shop_info.url), json=response)
    lat, lon = Decimal("0"), Decimal("0")

    # Act
    shop_info = vkusvill_api.get_shop_info(lat, lon)

    # Assert
    assert shop_info is None
