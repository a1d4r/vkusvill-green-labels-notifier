from decimal import Decimal

from httpx import Response
from respx import MockRouter

from vkusvill_green_labels.core.settings import VkusvillSettings
from vkusvill_green_labels.services.vkusvill_api import VkusvillApi


async def test_create_token(
    vkusvill_settings: VkusvillSettings,
    vkusvill_api: VkusvillApi,
    respx_mock: MockRouter,
    load_json,
):
    # Arrange
    respx_mock.post(str(vkusvill_settings.create_token.url)).mock(
        return_value=Response(200, json=load_json("token_response.json"))
    )

    # Act
    token_data = await vkusvill_api.create_new_user_token()

    # Assert
    assert token_data.token == "jwt_token"
    assert token_data.user_number == "&\\123456"


async def test_get_address_info(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    respx_mock: MockRouter,
    load_json,
):
    # Arrange
    respx_mock.get(str(vkusvill_settings.address_info.url)).mock(
        return_value=Response(200, json=load_json("address_info.json"))
    )
    lat, lon = Decimal("55.72673"), Decimal("37.622145")

    # Act
    address_info = await authorized_vkusvill_api.get_address_info(lat, lon)

    # Assert
    assert address_info is not None
    assert address_info.latitude == lat
    assert address_info.longitude == lon
    assert address_info.address == "Москва, Люсиновская улица, 6"
    assert address_info.res == 1


async def test_get_address_info_not_found(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    respx_mock: MockRouter,
    load_json,
):
    # Arrange
    respx_mock.get(str(vkusvill_settings.address_info.url)).mock(
        return_value=Response(200, json=load_json("address_info_not_found.json"))
    )
    lat, lon = Decimal("0"), Decimal("0")

    # Act
    address_info = await authorized_vkusvill_api.get_address_info(lat, lon)

    # Assert
    assert address_info is None


async def test_get_shop_info(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    respx_mock: MockRouter,
    load_json,
):
    # Arrange
    respx_mock.get(str(vkusvill_settings.shop_info.url)).mock(
        return_value=Response(200, json=load_json("shop_info.json"))
    )
    lat, lon = Decimal("55.72673"), Decimal("37.622145")

    # Act
    shop_info = await authorized_vkusvill_api.get_shop_info(lat, lon)

    # Assert
    assert shop_info is not None
    assert shop_info.shop_number == 8145


async def test_get_shop_info_not_found(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    respx_mock: MockRouter,
    load_json,
):
    # Arrange
    respx_mock.get(str(vkusvill_settings.shop_info.url)).mock(
        return_value=Response(200, json=load_json("shop_info_not_found.json"))
    )
    lat, lon = Decimal("0"), Decimal("0")

    # Act
    shop_info = await authorized_vkusvill_api.get_shop_info(lat, lon)

    # Assert
    assert shop_info is None


async def test_fetch_green_labels(
    vkusvill_settings: VkusvillSettings,
    authorized_vkusvill_api: VkusvillApi,
    respx_mock: MockRouter,
    load_json,
):
    # Arrange
    response_page_1 = load_json("green_labels.json")
    response_page_2 = load_json("green_labels_2.json")

    route = respx_mock.get(str(vkusvill_settings.green_labels.url))
    route.side_effect = [Response(200, json=response_page_1), Response(200, json=response_page_2)]

    # Act
    green_labels_items = await authorized_vkusvill_api.fetch_green_labels()

    # Assert
    assert len(green_labels_items) == 207
    assert green_labels_items[0].item_id == 88860
    assert green_labels_items[0].title == "Азу из филе грудки индейки, 500 г"
    assert green_labels_items[0].amount == Decimal("1")
    assert green_labels_items[0].weight_str == "500 г"
    assert green_labels_items[0].rating == "4.9"
    assert green_labels_items[0].price == Decimal("381")
    assert green_labels_items[0].discount_price == Decimal("229")
