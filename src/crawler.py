import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

from playwright.async_api import async_playwright, BrowserContext as PlaywrightBrowserContext, TimeoutError as PlaywrightTimeoutError
from html_to_markdown import convert, ConversionOptions

from sites import Site, Page



class Crawler:
    @staticmethod
    async def _fetch_static_html(session: aiohttp.ClientSession, page: Page, semaphore: asyncio.Semaphore | None) -> None:
        try:
            if semaphore:
                await semaphore.acquire() # Done manually to allow optional semaphore
            acquired = True
        
            async with session.get(page.url) as response:
                page.html = await response.text()

        finally:
            if semaphore and acquired:
                semaphore.release()


    @staticmethod
    async def _fetch_dynamic_html(context: PlaywrightBrowserContext, page: Page, semaphore: asyncio.Semaphore | None) -> None:
        try:
            if semaphore:
                await semaphore.acquire() # Done manually to allow optional semaphore
            acquired = True

            playwright_page = await context.new_page() # Creating a new page here is faster as page load can be started immediately

            try:
                await playwright_page.goto(page.url, wait_until="load", timeout=10000)
            except PlaywrightTimeoutError:
                pass # Pass because parts of page might still have loaded

            page.html = await playwright_page.content()

            await playwright_page.close()

        finally:
            if semaphore and acquired:
                semaphore.release()


    @staticmethod
    def _parse_html_to_txt(page: Page) -> None:


    @staticmethod
    async def crawl_site(site: Site, mode: Literal['static', 'dynamic'] = "static", concurrent_instances: int | None = 10) -> None:
        semaphore = asyncio.Semaphore(concurrent_instances) if concurrent_instances else None
        
        if mode == "static":
            async with aiohttp.ClientSession() as session:
                tasks = [Crawler._fetch_static_html(session, page, semaphore) for page in site.pages]
                await asyncio.gather(*tasks)
        elif mode == "dynamic":
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                context = await browser.new_context()

                await context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())

                tasks = [Crawler._fetch_dynamic_html(context, page, semaphore) for page in site.pages]
                await asyncio.gather(*tasks)

                await context.close()
                await browser.close()

        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(Crawler.__parse_html_to_txt, site.pages)
