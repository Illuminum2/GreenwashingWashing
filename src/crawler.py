import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor

from playwright.async_api import async_playwright, BrowserContext as PlaywrightBrowserContext, TimeoutError as PlaywrightTimeoutError
from html_to_markdown import convert, ConversionOptions

from sites import Site, Page



class Crawler:
    @staticmethod
    async def __fetch_static_html(session: aiohttp.ClientSession, page: Page) -> None:
        async with session.get(page.url) as response:
            page.html = await response.text()


    @staticmethod
    async def __fetch_dynamic_html(self, context: PlaywrightBrowserContext, page: Page, max_instances=10) -> None:
        playwright_page = await context.new_page() # Creating a new page here is faster as page load can be started immediately

        try:
            await playwright_page.goto(page.url, wait_until="load", timeout=10000)
        except PlaywrightTimeoutError:
            pass # Pass because parts of page might still have loaded

        page.html = await playwright_page.content()


    @staticmethod
    def __parse_html_to_txt(page: Page) -> None:
        page.content = convert(page.html, ConversionOptions(output_format="plain")).content # Parse HTML to text


    @staticmethod
    async def crawl_site(site: Site, mode="static") -> None:
        if mode == "static":
            async with aiohttp.ClientSession() as session:
                tasks = [Crawler.__fetch_static_html(session, page) for page in site.pages]
                await asyncio.gather(*tasks)
        elif mode == "dynamic":
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                context = await browser.new_context()

                await context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())

                tasks = [Crawler.__fetch_dynamic_html(context, page) for page in site.pages]
                await asyncio.gather(*tasks)

                await context.close()
                await browser.close()

        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(Crawler.__parse_html_to_txt, site.pages)
