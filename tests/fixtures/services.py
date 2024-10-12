import pytest

from vkusvill_green_labels.repositories.filter import FilterRepository
from vkusvill_green_labels.repositories.user import UserRepository
from vkusvill_green_labels.services.filter_service import FilterService
from vkusvill_green_labels.services.user_service import UserService


@pytest.fixture
def user_service(user_repository: UserRepository) -> UserService:
    return UserService(user_repository)


@pytest.fixture
def filter_service(user_service: UserService, filter_repository: FilterRepository) -> FilterService:
    return FilterService(user_service=user_service, filter_repository=filter_repository)
