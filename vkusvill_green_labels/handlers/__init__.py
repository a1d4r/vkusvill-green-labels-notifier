from vkusvill_green_labels.handlers.command import router as command_router
from vkusvill_green_labels.handlers.filters import router as filter_router
from vkusvill_green_labels.handlers.location import router as location_router
from vkusvill_green_labels.handlers.menu import router as menu_router
from vkusvill_green_labels.handlers.notifications import router as notifications_router

__all__ = (
    "command_router",
    "location_router",
    "notifications_router",
    "filter_router",
    "menu_router",
)
