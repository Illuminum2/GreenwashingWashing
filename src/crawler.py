import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

from playwright.async_api import async_playwright, BrowserContext as PlaywrightBrowserContext, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
from html_to_markdown import convert, ConversionOptions

from sites import Site, Page



class Crawler:
    @staticmethod
    async def _fetch_static_html(page: Page, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore | None) -> None:
        try:
            if semaphore:
                await semaphore.acquire() # Done manually to allow optional semaphore
            acquired = True

            try:
                async with session.get(page.url) as response:
                    page.html = await response.text()
            except aiohttp.ClientResponseError as e:
                print(f"Response exception '{type(e)}' was raised while accessing {page.url}: {e}")
            except aiohttp.ClientConnectionError as e:
                print(f"Connection exception '{type(e)}' was raised while accessing {page.url}: {e}")
            except aiohttp.ClientPayloadError as e:
                print(f"Payload exception '{type(e)}' was raised while accessing {page.url}: {e}")
            except Exception as e:
                print(f"Exception '{type(e)}' was raised while accessing {page.url}: {e}")

        finally:
            if semaphore and acquired:
                semaphore.release()


    @staticmethod
    async def _fetch_dynamic_html(page: Page, context: PlaywrightBrowserContext, semaphore: asyncio.Semaphore | None) -> None:
        try:
            if semaphore:
                await semaphore.acquire() # Done manually to allow optional semaphore
            acquired = True

            playwright_page = await context.new_page() # Creating a new page here is faster as page load can be started immediately

            try:
                try:
                    await playwright_page.goto(page.url, wait_until="load", timeout=10000)
                except PlaywrightTimeoutError: # Parts of page might still have loaded
                    print(f"Playwright timeout exception was raised while accessing {page.url}, attempting to parse what loaded. Increasing timeout might help.")

                page.html = await playwright_page.content()
            except PlaywrightError as e:
                print(f"Playwright exception '{e.name}' was raised while accessing {page.url}: {e.message}")
            except Exception as e:
                print(f"Exception '{type(e)}' was raised while accessing {page.url}: {e}")

            await playwright_page.close()

        finally:
            if semaphore and acquired:
                semaphore.release()


    @staticmethod
    def _parse_html_to_txt(page: Page) -> None:
        if page.html:
            page.content = convert(page.html, ConversionOptions(output_format="plain")).content # Parse HTML to text


    @staticmethod
    async def crawl_site(site: Site, mode: Literal['static', 'dynamic'] = "static", concurrent_instances: int | None = 10) -> None:
        semaphore = asyncio.Semaphore(concurrent_instances) if concurrent_instances else None
        
        if mode == "static":
            async with aiohttp.ClientSession() as session:
                tasks = [Crawler._fetch_static_html(page, session, semaphore) for page in site.pages]
                await asyncio.gather(*tasks)
        elif mode == "dynamic":
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                context = await browser.new_context()

                await context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())

                tasks = [Crawler._fetch_dynamic_html(page, context, semaphore) for page in site.pages]
                await asyncio.gather(*tasks)

                await context.close()
                await browser.close()

        with ThreadPoolExecutor(max_workers=concurrent_instances) as executor:
            executor.map(Crawler._parse_html_to_txt, site.pages)
