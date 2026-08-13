import asyncio
from typing import Any, Literal

from diskcache import Cache as DiskCache

from config import CACHE_PATH, CACHE_EXPIRY_S



# https://github.com/grantjenks/python-diskcache/issues/282
class Cache:
    def __init__(self, subfolder: str | None = None):
        self._cache = DiskCache(f"{CACHE_PATH}/{subfolder}")


    async def store(self, item: Any, value: Any, expire: float | None = CACHE_EXPIRY_S) -> Literal[True]:
        #return self._cache.set(item, value, expire=expire)
        return await asyncio.get_running_loop().run_in_executor(None, self._cache.set, item, value, expire)

    
    async def retreive(self, item: Any) -> Any:
        #return self._cache.get(item)
        return await asyncio.get_running_loop().run_in_executor(None, self._cache.get, item)


    async def close(self) -> None:
        await asyncio.get_running_loop().run_in_executor(None, self._cache.expire)
        self._cache.close()
