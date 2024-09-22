from vkusvill_green_labels.dependencies import container
from vkusvill_green_labels.services.updater_service import UpdaterService


async def check_green_labels() -> None:
    async with container() as request_container:
        updater_service = await request_container.get(UpdaterService)
        await updater_service.update_green_labels()
