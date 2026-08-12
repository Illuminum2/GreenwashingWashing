import asyncio
from typing import Literal

from html_to_markdown import convert, ConversionOptions
from lxml import etree

from network import Network
from matcher import Matcher

from sites import Site, Page

from config import SCRAPING_MODE


class Crawler:
    @staticmethod
    async def _fetch_page(page: Page, network: Network) -> None:
        page.raw = await network.fetch_url(page.url)


    @staticmethod
    def _parse_xml_page(page: Page) -> list[str] | None:
        if page.raw is not None:
            parser = etree.XMLParser(remove_blank_text=True)
            xml = etree.XML(bytes(page.raw, encoding="utf-8"), parser)
            page.links = xml.xpath("//*[local-name() = 'loc']/text()")

            return page.links


    @staticmethod
    def _parse_html_page(page: Page) -> list[str] | None:
        if page.raw is not None:
            result = convert(page.raw, ConversionOptions(output_format="plain", skip_images=True)) # Parse HTML to text
            page.content = result.content
            page.links = [link.href for link in result.metadata.links]

            return page.links
    

    @staticmethod
    async def crawl_page(page: Page, network: Network) -> list[str] | None:
        await Crawler._fetch_page(page, network)

        if Matcher.isXMLUrl(page.url):
            return await asyncio.get_running_loop().run_in_executor(None, Crawler._parse_xml_page, page)
        
        return await asyncio.get_running_loop().run_in_executor(None, Crawler._parse_html_page, page)


    @staticmethod
    async def crawl_page_recursive(page: Page, out_q: asyncio.Queue, tg: asyncio.TaskGroup, network: Network) -> None:
        links = await Crawler.crawl_page(page, network)

        for link in links:
            if (link_page := page.site.add_page(link)):
                tg.create_task(Crawler.crawl_page_recursive(link_page, out_q, tg, network))

        await out_q.put(page)


    @staticmethod
    async def crawl_site(site: Site, out_q: asyncio.Queue, mode: Literal['static', 'dynamic'] = SCRAPING_MODE) -> None:
        async with Network(mode=mode) as network:
            async with asyncio.TaskGroup() as tg:
                [tg.create_task(Crawler.crawl_page_recursive(page, out_q, tg, network)) for page in site.pages]

        await out_q.shutdown()
