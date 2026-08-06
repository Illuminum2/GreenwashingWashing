import re
import requests

from bs4 import BeautifulSoup

from sites import Site, Page

def __crawl_sitemap(sitemap_url: str) -> list[str]:
    page = requests.get(sitemap_url)
    xmlSoup = BeautifulSoup(page.content, features="lxml")

    url_elements = xmlSoup.find_all('loc') # Extract all link elements from sitemap
    return [url.text for url in url_elements] # Extract links from all link elements



def map_site(base_url: str, sitemap_path="/sitemap.xml") -> Site:
    sitemap_urls = [base_url + sitemap_path]
    site = Site(base_url)

    xml_prog = re.compile(r"[^?]+\.xml") # Pattern for matching XML sitemaps
    
    i = 0
    while i < len(sitemap_urls):
        res_urls = __crawl_sitemap(sitemap_urls[i])

        for url in res_urls:
            if not xml_prog.match(url):
                if url not in site.page_urls():
                    site.pages.append(Page(url))
            elif url not in sitemap_urls:
                sitemap_urls.append(url)
        
        i += 1

    return site
