import asyncio
from typing import Literal

from html_to_markdown import convert, ConversionOptions
from lxml import etree

from gww.network.network import Network, HTTPError, NetworkError

from gww.data.sites import Site, Page
from gww.network.url import Url

from gww.utils.config import Config


class Crawler:
    @staticmethod
    async def _fetch_page(page: Page, network: Network) -> None:
        try:
            page.raw = await network.fetch_url(page.url)
        except (HTTPError, NetworkError, UnicodeDecodeError) as e:
            page.errors.append(str(e))


    @staticmethod
    def _parse_xml_page(page: Page) -> list[Url] | None:
        if page.raw is not None and page.raw != '': # Empty content throws lxml exception
            parser = etree.XMLParser(remove_blank_text=True)
            xml = etree.XML(bytes(page.raw, encoding="utf-8"), parser)
            page.links = Url.parse_urls(xml.xpath("//*[local-name() = 'loc']/text()"), page.url)

            return page.links


    @staticmethod
    def _parse_html_page(page: Page) -> list[Url] | None:
        if page.raw is not None:
            result = convert(page.raw, ConversionOptions(output_format="plain", skip_images=True)) # Parse HTML to text
            page.content = result.content
            page.links = Url.parse_urls([link.href for link in result.metadata.links], page.url)

            return page.links
    

    @staticmethod
    async def crawl_page(page: Page, network: Network) -> list[Url] | None:
        await Crawler._fetch_page(page, network)

        try:
            if page.url.is_XML:
                return await asyncio.get_running_loop().run_in_executor(None, Crawler._parse_xml_page, page)
            
            return await asyncio.get_running_loop().run_in_executor(None, Crawler._parse_html_page, page)
        except Exception as e:
            page.errors.append(str(e))


    @staticmethod
    async def crawl_page_recursive(page: Page, out_q: asyncio.Queue[Page], tg: asyncio.TaskGroup, network: Network, depth: int = 0) -> None:
        links = await Crawler.crawl_page(page, network)

        if links is not None:
            for link in links:
                if link_page := page.site.add_page(link, depth + 1):
                    tg.create_task(Crawler.crawl_page_recursive(link_page, out_q, tg, network, depth+1))

        await out_q.put(page)


    @staticmethod
    async def run(site: Site, out_q: asyncio.Queue[Page], mode: Literal['static', 'dynamic'] = Config.get("crawl.default_mode", "static")) -> None:
        try:
            async with Network.get(mode=mode) as network:
                async with asyncio.TaskGroup() as tg:
                    [tg.create_task(Crawler.crawl_page_recursive(page, out_q, tg, network)) for page in site.pages]

        finally:
            out_q.shutdown()
