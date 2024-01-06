import sys
import asyncio
from .http import *

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()
    )