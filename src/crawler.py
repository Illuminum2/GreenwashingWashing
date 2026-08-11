import asyncio
from typing import Literal

from playwright.async_api import async_playwright, BrowserContext as PlaywrightBrowserContext, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
from html_to_markdown import convert, ConversionOptions

from network import Network

from sites import Site, Page

from config import SCRAPING_MODE


class Crawler:
    @staticmethod
    async def _fetch_page_html(page: Page, network: Network) -> None:
        page.html = await network.fetch_url(page.url)


    @staticmethod
    def _parse_html_to_txt(page: Page) -> None:
        if page.html is not None:
            page.content = convert(page.html, ConversionOptions(output_format="plain")).content # Parse HTML to text


    @staticmethod
    async def crawl_site(site: Site, mode: Literal['static', 'dynamic'] = SCRAPING_MODE) -> None:
        async with Network(mode=mode) as network:
            tasks = [Crawler._fetch_page_html(page, network) for page in site.pages]
            await asyncio.gather(*tasks)

        for page in site.pages:
            asyncio.get_running_loop().run_in_executor(None, Crawler._parse_html_to_txt, page)
