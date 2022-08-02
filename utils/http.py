from aiohttp import ClientSession
import asyncio


async def aio_get(url: str, *args, **kwargs) -> bytes:
    async with ClientSession() as Session:
        async with Session.get(url, *args, **kwargs) as resp:
            return await resp.read()


async def aio_size(url: str) -> int:
    async with ClientSession() as Session:
        async with Session.head(url) as resp:
            return int(resp.headers['Content-Length'])