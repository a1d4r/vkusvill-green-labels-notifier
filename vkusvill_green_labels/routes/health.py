from aiohttp import web


async def health(request: web.Request) -> web.Response:  # noqa: ARG001
    return web.Response(status=200)
