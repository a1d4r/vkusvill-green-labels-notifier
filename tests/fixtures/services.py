import pytest

from vkusvill_green_labels.repositories.user import UserRepository
from vkusvill_green_labels.services.user_service import UserService


@pytest.fixture
def user_service(user_repository: UserRepository) -> UserService:
    return UserService(user_repository)
