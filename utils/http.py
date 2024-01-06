import asyncio
from httpx import AsyncClient
from random import random


count = 0
client = AsyncClient()
semaphore = asyncio.Semaphore(1)


async def aio_get(url: str, *args, **kwargs) -> tuple[bytes, int]:
    global count
    async with semaphore:
        await asyncio.sleep(random() * 0.5)
        resp = await client.get(url, *args, **kwargs)
    count += 1
    return resp.content, resp.status_code


async def aio_size(url: str) -> int:
    resp = await client.head(url)
    return int(resp.headers['Content-Length'])


def get_count():
    global count
    return count