from aiogram.types import User as TelegramUser
from faker import Faker
from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from vkusvill_green_labels.models.db import Location, User, UserSettings
from vkusvill_green_labels.models.types import Latitude, Longitude
from vkusvill_green_labels.models.vkusvill import AddressInfo


class TelegramUserFactory(ModelFactory[TelegramUser]):
    __faker__ = Faker(locale="ru_RU")
    __model__ = TelegramUser
    __set_as_default_factory_for_type__ = True

    @classmethod
    def first_name(cls) -> str:
        return cls.__faker__.first_name()

    @classmethod
    def last_name(cls) -> str:
        return cls.__faker__.last_name()

    @classmethod
    def username(cls) -> str:
        return cls.__faker__.user_name()

    @classmethod
    def language_code(cls) -> str:
        return cls.__faker__.language_code()


class AddressInfoFactory(ModelFactory[AddressInfo]):
    __faker__ = Faker(locale="ru_RU")
    __model__ = AddressInfo
    __set_as_default_factory_for_type__ = True

    @classmethod
    def latitude(cls) -> Latitude:
        return Latitude(cls.__faker__.latitude())

    @classmethod
    def longitude(cls) -> Longitude:
        return Longitude(cls.__faker__.longitude())

    @classmethod
    def address(cls) -> str:
        return cls.__faker__.address()


class LocationFactory(SQLAlchemyFactory[Location]):
    __model__ = Location
    __faker__ = Faker(locale="ru_RU")
    __set_as_default_factory_for_type__ = True

    @classmethod
    def latitude(cls) -> Latitude:
        return Latitude(cls.__faker__.latitude())

    @classmethod
    def longitude(cls) -> Longitude:
        return Longitude(cls.__faker__.longitude())

    @classmethod
    def address(cls) -> str:
        return cls.__faker__.address()


class UserSettingsFactory(SQLAlchemyFactory[UserSettings]):
    __faker__ = Faker(locale="ru_RU")
    __model__ = UserSettings
    __set_as_default_factory_for_type__ = True

    id = Ignore()
    vkusvill_settings = Ignore()


class UserFactory(SQLAlchemyFactory[User]):
    __model__ = User
    __faker__ = Faker(locale="ru_RU")
    __set_relationships__ = True
    __set_as_default_factory_for_type__ = True

    id = Ignore()
    user_settings_id = Ignore()
    user_settings = UserSettingsFactory

    @classmethod
    def first_name(cls) -> str:
        return cls.__faker__.first_name()

    @classmethod
    def last_name(cls) -> str:
        return cls.__faker__.last_name()

    @classmethod
    def username(cls) -> str:
        return cls.__faker__.user_name()
