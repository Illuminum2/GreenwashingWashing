import asyncio
from typing import AsyncIterator

class Pipeline:
    @staticmethod
    async def queue_drain[T](q: asyncio.Queue[T]) -> AsyncIterator[T]:
        while True:
            try:
                yield await q.get()
            except asyncio.QueueShutDown:
                return
