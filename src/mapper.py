import re
import requests

from bs4 import BeautifulSoup

from sites import Site, Page



class Mapper:
    @staticmethod
    def _crawl_sitemap(sitemap_url: str) -> list[str]:
        page = requests.get(sitemap_url)
        xmlSoup = BeautifulSoup(page.content, features="xml")

        url_elements = xmlSoup.find_all('loc') # Extract all link elements from sitemap
        return [url.text for url in url_elements] # Extract links from all link elements


    @staticmethod
    def map_site(site: Site, sitemap_path: str = "/sitemap.xml") -> None:
        sitemap_urls = [site.base_url + sitemap_path]

        xml_prog = re.compile(r"[^?]+\.xml") # Pattern for matching XML sitemaps
        
        i = 0
        while i < len(sitemap_urls):
            res_urls = Mapper._crawl_sitemap(sitemap_urls[i])

            for url in res_urls:
                if not xml_prog.match(url):
                    if url not in site.page_urls():
                        site.pages.append(Page(url))
                elif url not in sitemap_urls:
                    sitemap_urls.append(url)
            
            i += 1
