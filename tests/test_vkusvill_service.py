from decimal import Decimal

from requests_mock import Mocker

from vkusvill_green_labels.services.vkusvill import VkusvillApi
from vkusvill_green_labels.settings import VkusvillSettings


def test_create_token(
    vkusvill_settings: VkusvillSettings, vkusvill_api: VkusvillApi, requests_mock: Mocker, load_json
):
    # Arrange
    response = load_json("token_response.json")
    requests_mock.post(str(vkusvill_settings.create_token.url), json=response)

    # Act
    token_data = vkusvill_api.create_new_user_token()

    # Assert
    assert token_data.token == "jwt_token"
    assert token_data.user_number == "&\\123456"


def test_get_address_info(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    requests_mock: Mocker,
    load_json,
):
    # Arrange
    response = load_json("address_info.json")
    requests_mock.get(str(vkusvill_settings.address_info.url), json=response)
    lat, lon = Decimal("55.72673"), Decimal("37.622145")

    # Act
    address_info = authorized_vkusvill_api.get_address_info(lat, lon)

    # Assert
    assert address_info is not None
    assert address_info.latitude == lat
    assert address_info.longitude == lon
    assert address_info.address == "Москва, Люсиновская улица, 6"
    assert address_info.res == 1


def test_get_address_info_not_found(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    requests_mock: Mocker,
    load_json,
):
    # Arrange
    response = load_json("address_info_not_found.json")
    requests_mock.get(str(vkusvill_settings.address_info.url), json=response)
    lat, lon = Decimal("0"), Decimal("0")

    # Act
    address_info = authorized_vkusvill_api.get_address_info(lat, lon)

    # Assert
    assert address_info is None


def test_get_shop_info(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    requests_mock: Mocker,
    load_json,
):
    # Arrange
    response = load_json("shop_info.json")
    requests_mock.get(str(vkusvill_settings.shop_info.url), json=response)
    lat, lon = Decimal("55.72673"), Decimal("37.622145")

    # Act
    shop_info = authorized_vkusvill_api.get_shop_info(lat, lon)

    # Assert
    assert shop_info is not None
    assert shop_info.shop_number == 8145


def test_get_shop_info_not_found(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    requests_mock: Mocker,
    load_json,
):
    # Arrange
    response = load_json("shop_info_not_found.json")
    requests_mock.get(str(vkusvill_settings.shop_info.url), json=response)
    lat, lon = Decimal("0"), Decimal("0")

    # Act
    shop_info = authorized_vkusvill_api.get_shop_info(lat, lon)

    # Assert
    assert shop_info is None


def test_fetch_green_labels(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    requests_mock: Mocker,
    load_json,
):
    # Arrange
    response_page_1 = load_json("green_labels.json")
    response_page_2 = load_json("green_labels_2.json")

    response_list = [
        {"json": response_page_1, "status_code": 200},
        {"json": response_page_2, "status_code": 200},
    ]

    requests_mock.get(str(vkusvill_settings.green_labels.url), response_list=response_list)

    # Act
    green_labels_items = authorized_vkusvill_api.fetch_green_labels()

    # Assert
    assert len(green_labels_items) == 200
    assert green_labels_items[0].item_id == 88860
    assert green_labels_items[0].title == "Азу из филе грудки индейки, 500 г"
    assert green_labels_items[0].amount == Decimal("1")
    assert green_labels_items[0].weight_str == "500 г"
    assert green_labels_items[0].rating == "4.9"
    assert green_labels_items[0].price == Decimal("381")
    assert green_labels_items[0].discount_price == Decimal("229")
