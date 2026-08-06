from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

import re

from playwright.sync_api import sync_playwright
from html_to_markdown import convert, ConversionOptions


SITE_URL = "https://books.toscrape.com"

MATCH_SPECIFICATION = [
    'öko',
    'bio',
    'umwe',
    'grün',
    'achhal',
    'neuerb',
    'emission',
    'eutr',
    'ergi',
    'strom',
]



@dataclass
class Site:
    url: str
    content: str



def crawl_sitemap(sitemap_url):
    page = requests.get(sitemap_url)
    xmlSoup = BeautifulSoup(page.content, features="xml")

    result_urls = xmlSoup.find_all('loc')
    res = []
    for url in result_urls:
        res.append(url.contents[0])

    return res



def obtain_site_urls(url):
    sitemap_urls = [f"{url}/sitemap.xml"]
    prog = re.compile(r"[^?]+\.xml")

    site_urls = []
    
    i = 0
    while i < len(sitemap_urls):
        res = crawl_sitemap(sitemap_urls[i])

        for r in res:
            if not prog.match(r):
                if r not in site_urls:
                    site_urls.append(r)
            elif r not in sitemap_urls:
                sitemap_urls.append(r)
        
        i += 1

    return site_urls



def playwright_crawl(urls):
    res = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        for url in urls:
            try:
                page.goto(url, wait_until="load", timeout=5000)
            except: # Do NOT do this
                pass

            content_html = str(BeautifulSoup(page.content(), 'lxml').body) # Get only HTML within body tag
            content_txt = convert(content_html, ConversionOptions(output_format="plain")).content # Parsed text from HTML

            res.append(Site(url, content_txt))

        browser.close()

    return res



def request_crawl(urls):
    res = []

    for url in urls:
        page = requests.get(url)

        content_html = str(BeautifulSoup(page.content, 'lxml').body) # Get only HTML within body tag
        content_txt = convert(content_html, ConversionOptions(output_format="plain")).content # Parsed text from HTML

        res.append(Site(url, content_txt))

    return res



def match_sites(prog, sites):
    matches = {}

    for site in sites:
        for word in site.content.split():
            if prog.search(word):
                if not site.url in matches:
                    matches[site.url] = []
                matches[site.url].append(word)

    return matches



if __name__ == '__main__':
    urls = obtain_site_urls(SITE_URL)

    sites = playwright_crawl(urls)

    pattern = '|'.join('(%s)' % case for case in MATCH_SPECIFICATION)
    prog = re.compile(pattern, re.I)
    print(match_sites(prog, sites))
