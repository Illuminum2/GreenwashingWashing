import re
import requests


from bs4 import BeautifulSoup



def __crawl_sitemap(sitemap_url):
    page = requests.get(sitemap_url)
    xmlSoup = BeautifulSoup(page.content, features="xml")

    result_urls = xmlSoup.find_all('loc')
    res = []
    for url in result_urls:
        res.append(url.contents[0])

    return res



def map_site(url):
    sitemap_urls = [f"{url}/sitemap.xml"]
    prog = re.compile(r"[^?]+\.xml")

    site_urls = []
    
    i = 0
    while i < len(sitemap_urls):
        res = __crawl_sitemap(sitemap_urls[i])

        for r in res:
            if not prog.match(r):
                if r not in site_urls:
                    site_urls.append(r)
            elif r not in sitemap_urls:
                sitemap_urls.append(r)
        
        i += 1

    return site_urls
