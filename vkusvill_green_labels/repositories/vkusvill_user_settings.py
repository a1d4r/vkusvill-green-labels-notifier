import abc

from vkusvill_green_labels.services.vkusvill import VkusvillUserSettings


class VkusvillUserSettingsRepository(abc.ABC):
    @abc.abstractmethod
    def get_settings(self) -> VkusvillUserSettings | None: ...

    @abc.abstractmethod
    def set_settings(self, user_settings: VkusvillUserSettings) -> None: ...


class InMemoryVkusvillUserSettingsRepository(VkusvillUserSettingsRepository):
    def __init__(self) -> None:
        self.user_settings: VkusvillUserSettings | None = None

    def get_settings(self) -> VkusvillUserSettings | None:
        return self.user_settings

    def set_settings(self, user_settings: VkusvillUserSettings) -> None:
        self.user_settings = user_settings
