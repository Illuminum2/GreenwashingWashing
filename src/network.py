import aiohttp
import asyncio
from contextlib import nullcontext, suppress
from typing import Literal, Self

from playwright.async_api import async_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeout

from config import CONCURRENT_NETWORK_REQUESTS, DEFAULT_NETWORK_MODE, DYNAMIC_SCRAPE_TIMEOUT, STATIC_SCRAPE_TIMEOUT


class HTTPError(Exception):
    def __init__(self, status: int, reason: str, url: str) -> None:
        super().__init__(reason)
        self.status = status
        self.reason = reason
        self.url = url

    def __str__(self) -> str:
        return f"Got response status code '{self.status}: {self.reason}' while trying to access '{self.url}'"



class NetworkError(Exception):
    def __init__(self, text: str, url: str) -> None:
        super().__init__(text)
        self.text = text

    def __str__(self) -> str:
        return self.text



class Network:
    _semaphore: asyncio.Semaphore | None = (
        asyncio.Semaphore(CONCURRENT_NETWORK_REQUESTS)
        if CONCURRENT_NETWORK_REQUESTS is not None and CONCURRENT_NETWORK_REQUESTS > 0
        else None
    )


    def __init__(self, mode: Literal['static', 'dynamic'] = DEFAULT_NETWORK_MODE) -> None:
        self._mode = mode
        self._session: aiohttp.ClientSession | None = None
        self._context = None
        self._playwright, self._browser = None, None


    async def fetch_url(self, url: str) -> str | None:
        # https://stackoverflow.com/a/73556999
        semaphore = self._semaphore if self._semaphore else nullcontext()

        async with semaphore:
            try:
                if self._mode == "static" and self._session:
                    async with self._session.get(url) as response:
                        if not response.ok:
                            raise HTTPError(response.status, response.reason, url)

                        return await response.text()
                
                if self._mode == "dynamic" and self._context:
                    playwright_page = await self._context.new_page() # Creating a new page here is faster as page load can be started immediately

                    try:
                        try:
                            response = await playwright_page.goto(url, wait_until="load", timeout=DYNAMIC_SCRAPE_TIMEOUT)
                        except PlaywrightTimeout:
                            print(f"Reached timeout on '{url}', proceeding with partial content")

                        if 'response' in locals() and not response.status < 400:
                            raise HTTPError(response.status, response.status_text, url)
                        
                        return await playwright_page.content()
                    finally:
                        await playwright_page.close()

            except HTTPError as e:
                print(e)
                raise e
            except (aiohttp.ClientError, PlaywrightError) as e:
                print(f"Exception '{type(e)}' was raised while trying to accessing '{url}': {e}")
                raise NetworkError(str(e))


    async def __aenter__(self) -> Self:
        if self._mode == "static":
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=STATIC_SCRAPE_TIMEOUT / 1000))
        elif self._mode == "dynamic":
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch()
            self._context = await self._browser.new_context()

            await self._context.route(
                "**/*",
                lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_()
            )

        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._session:
            with suppress(Exception): await self._session.close()
        if self._context:
            with suppress(Exception): await self._context.close()
        if self._browser:
            with suppress(Exception): await self._browser.close()
        if self._playwright:
            with suppress(Exception): await self._playwright.stop()
