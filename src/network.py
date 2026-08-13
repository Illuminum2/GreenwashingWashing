import aiohttp
import asyncio
from abc import ABC, abstractmethod
from contextlib import nullcontext, suppress
from typing import Literal, Self

from playwright.async_api import async_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeout
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception, retry_if_exception_type

from url import Url

from config import CONCURRENT_NETWORK_REQUESTS, MAX_NETWORK_RETRIES, MIN_NETWORK_RETRY_DELAY, MAX_NETWORK_RETRY_DELAY, DEFAULT_NETWORK_MODE, DYNAMIC_SCRAPE_TIMEOUT_MS, STATIC_SCRAPE_TIMEOUT_MS


class HTTPError(Exception):
    def __init__(self, status: int, reason: str, url: Url) -> None:
        super().__init__(reason)
        self.status = status
        self.reason = reason
        self.url = url

    def __str__(self) -> str:
        return f"Got response status code '{self.status}: {self.reason}' while trying to access '{self.url}'"



class NetworkError(Exception):
    def __init__(self, text: str, url: Url) -> None:
        super().__init__(text)
        self.text = text
        self.url = url

    def __str__(self) -> str:
        return self.text



class Network(ABC):
    _semaphore: asyncio.Semaphore | None = None


    def __init__(self) -> None:
        pass


    def get(mode: Literal['static', 'dynamic'] = DEFAULT_NETWORK_MODE) -> Network:
        if mode == "dynamic":
            return DynamicNetwork()
        return StaticNetwork()


    @abstractmethod
    async def _fetch_url(self, url: Url) -> str:
        pass


    @retry(
        wait=wait_exponential_jitter(MIN_NETWORK_RETRY_DELAY, MAX_NETWORK_RETRY_DELAY),
        stop=stop_after_attempt(MAX_NETWORK_RETRIES),
        retry=(
            retry_if_exception(lambda e: type(e) is HTTPError and (e.status == 503 or e.status == 504))
            | retry_if_exception_type(NetworkError)
        ),
        reraise=True
    )
    async def fetch_url(self, url: Url) -> str:
        # https://stackoverflow.com/a/73556999
        semaphore = self._semaphore if self._semaphore else nullcontext()

        async with semaphore:
            try:
                return await self._fetch_url(url)

            except HTTPError as e:
                print(e)
                raise e
            except (aiohttp.ClientError, asyncio.TimeoutError, PlaywrightError) as e:
                print(f"Exception '{type(e)}' was raised while trying to accessing '{url}': {e}")
                raise NetworkError(str(e), url)


    async def __aenter__(self) -> Self:
        if self._semaphore is None and CONCURRENT_NETWORK_REQUESTS is not None:
            if CONCURRENT_NETWORK_REQUESTS == 0:
                raise ValueError("Concurrent network requests is set to 0, must be >1 or -1 for unlimited")
            
            self._semaphore = (
                asyncio.Semaphore(CONCURRENT_NETWORK_REQUESTS)
                if CONCURRENT_NETWORK_REQUESTS >= 1
                else None
            )

        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass



class StaticNetwork(Network):
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None


    async def _fetch_url(self, url: Url) -> str:
        async with self._session.get(url.string) as response:
            if not response.ok:
                raise HTTPError(response.status, response.reason, url)

            return await response.text(errors="replace")


    async def __aenter__(self) -> Self:
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=(STATIC_SCRAPE_TIMEOUT_MS / 1000)))

        await super().__aenter__()

        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        with suppress(Exception): await self._session.close()

        await super().__aexit__(exc_type, exc_val, exc_tb)



class DynamicNetwork(Network):
    def __init__(self) -> None:
        self._context = None
        self._browser = None
        self._playwright = None


    async def _fetch_url(self, url: Url) -> str:
        playwright_page = await self._context.new_page()
        
        try:
            response = None

            try:
                response = await playwright_page.goto(url.string, wait_until="load", timeout=DYNAMIC_SCRAPE_TIMEOUT_MS)
            except PlaywrightTimeout:
                print(f"Reached timeout on '{url}', proceeding with partial content")

            if response is not None and response.status >= 400:
                raise HTTPError(response.status, response.status_text, url)
            
            return await playwright_page.content()
        finally:
            await playwright_page.close()


    async def __aenter__(self) -> Self:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch()
        self._context = await self._browser.new_context()

        # Block images, videos, css, fonts etc. from loading
        await self._context.route(
            "**/*",
            lambda route: route.abort() if route.request.resource_type in ["image", "media", "stylesheet", "font"] else route.continue_()
        )
        
        await super().__aenter__()

        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        with suppress(Exception): await self._context.close()
        with suppress(Exception): await self._browser.close()
        with suppress(Exception): await self._playwright.stop()

        await super().__aexit__(exc_type, exc_val, exc_tb)
