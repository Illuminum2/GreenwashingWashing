import asyncio
from typing import Any, Literal

from diskcache import Cache as DiskCache

from utils.config import Config


# https://github.com/grantjenks/python-diskcache/issues/282
class Cache:
    _disabled: bool = False


    def __init__(self, subfolder: str | None = None):
        self._cache = DiskCache(f"{Config.get("cache.path", __file__ + '/../../cache/')}/{subfolder}")


    async def store(self, item: Any, value: Any, expire: float | None = Config.get("cache.expiry_s", 3600)) -> Literal[True]:
        #return self._cache.set(item, value, expire=expire)
        return await asyncio.get_running_loop().run_in_executor(None, self._cache.set, item, value, expire)

    
    async def retreive(self, item: Any) -> Any:
        if Cache._disabled is True:
            return None
        
        #return self._cache.get(item)
        return await asyncio.get_running_loop().run_in_executor(None, self._cache.get, item)


    async def close(self) -> None:
        await asyncio.get_running_loop().run_in_executor(None, self._cache.expire)
        self._cache.close()


    @staticmethod
    def disable():
        Cache._disabled = True
