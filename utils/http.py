import asyncio
from aiohttp import ClientSession
from random import random


count = 0


async def aio_get(url: str, *args, **kwargs) -> tuple[bytes, int]:
    global count
    async with ClientSession() as Session:
        async with Session.get(url, *args, **kwargs) as resp:
            count += 1
            return await resp.read(), resp.status


async def aio_size(url: str) -> int:
    async with ClientSession() as Session:
        async with Session.head(url) as resp:
            return int(resp.headers['Content-Length'])


def get_count():
    global count
    return count