import pytest

from aiogram.types import User as TelegramUser

from tests.factories import AddressInfoFactory, TelegramUserFactory
from vkusvill_green_labels.models.vkusvill import AddressInfo


@pytest.fixture
def telegram_user() -> TelegramUser:
    return TelegramUserFactory.build()


@pytest.fixture
def address_info() -> AddressInfo:
    return AddressInfoFactory.build()
