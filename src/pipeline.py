import asyncio
from typing import AsyncGenerator, Coroutine, Any

class Pipeline:
    @staticmethod
    async def queue_drain(q: asyncio.Queue) -> AsyncGenerator[Coroutine[Any, Any, Any]]:
        try:
            yield await q.get()
        except asyncio.QueueShutDown:
            return
