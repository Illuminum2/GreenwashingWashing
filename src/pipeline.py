import asyncio
from typing import AsyncIterator, Coroutine, Any

class Pipeline:
    @staticmethod
    async def queue_drain(q: asyncio.Queue) -> AsyncIterator[Coroutine[Any, Any, Any]]:
        try:
            yield await q.get()
        except asyncio.QueueShutDown:
            return
