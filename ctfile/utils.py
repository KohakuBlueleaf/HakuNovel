from aiohttp import ClientSession
import asyncio


CHUNK = 16384


async def get(url: str, *args, **kwargs) -> bytes:
    async with ClientSession() as Session:
        async with Session.get(url, *args, **kwargs) as resp:
            data = b''
            while (chunk := await resp.content.read(CHUNK)):
                data  += chunk
                await asyncio.sleep(0.000001)
            return data

async def size(url: str) -> int:
    async with ClientSession() as Session:
        async with Session.head(url) as resp:
            return int(resp.headers['Content-Length'])