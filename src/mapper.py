import re
import requests
from typing import Literal

from bs4 import BeautifulSoup

from network import Network

from sites import Site, Page


from config import MAPPING_MODE


class Mapper:
    @staticmethod
    async def _crawl_sitemap(url: str, mode: Literal['static', 'dynamic'] = MAPPING_MODE) -> list[str]:
        async with Network(mode=mode) as network:
            content = await network.fetch_url(url)

            xmlSoup = BeautifulSoup(content, features="xml")
            url_elements = xmlSoup.find_all('loc') # Extract all link elements from sitemap

            return [url.text for url in url_elements] # Extract links from all link elements


    @staticmethod
    async def map_site(site: Site, sitemap_path: str = "/sitemap.xml") -> None:
        sitemap_urls = [site.base_url + sitemap_path]

        xml_prog = re.compile(r"[^?]+\.xml") # Pattern for matching XML sitemaps
        
        i = 0
        while i < len(sitemap_urls):
            res_urls = await Mapper._crawl_sitemap(sitemap_urls[i])

            for url in res_urls:
                if not xml_prog.match(url):
                    if url not in site.page_urls():
                        site.pages.append(Page(url))
                elif url not in sitemap_urls:
                    sitemap_urls.append(url)
            
            i += 1
