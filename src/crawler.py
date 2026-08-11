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
    def _parse_xml_page(page: Page) -> None:
        if page.raw is not None:
            parser = etree.XMLParser(remove_blank_text=True)
            xml = etree.XML(bytes(page.raw, encoding="utf-8"), parser)
            #links = xml.xpath("//ns:loc/text()", namespaces={"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
            page.links = xml.xpath("//*[local-name() = 'loc']/text()")


    @staticmethod
    def _parse_html_page(page: Page) -> None:
        if page.raw is not None:
            result = convert(page.raw, ConversionOptions(output_format="plain", skip_images=True)) # Parse HTML to text
            page.content = result.content
            page.links = [link.href for link in result.metadata.links]
    

    @staticmethod
    async def crawl_page(page: Page, network: Network) -> None:
        await Crawler._fetch_page(page, network)

        if Matcher.isXMLUrl(page.url):
            await asyncio.get_running_loop().run_in_executor(None, Crawler._parse_xml_page, page)
        else:
            await asyncio.get_running_loop().run_in_executor(None, Crawler._parse_html_page, page)


    @staticmethod
    async def crawl_site(site: Site, mode: Literal['static', 'dynamic'] = SCRAPING_MODE) -> None:
        async with Network(mode=mode) as network:
            tasks = [Crawler.crawl_page(page, network) for page in site.pages]
            await asyncio.gather(*tasks)
