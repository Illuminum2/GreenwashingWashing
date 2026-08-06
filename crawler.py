import requests
from bs4 import BeautifulSoup

import re

from playwright.sync_api import sync_playwright
from html_to_markdown import convert, ConversionOptions

from pathlib import Path
import timeit


SITE_URL = "https://www.bluechip.at"

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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for (i, url) in enumerate(urls):
            try:
                page.goto(url, wait_until="load", timeout=5000)
                print(url)
            except: # Do NOT do this
                pass

            htmlSoup = BeautifulSoup(page.content(), 'lxml')

            with open(f"./results/{i}.html", "w", encoding="utf-8") as file:
                file.write(convert(str(htmlSoup.body), ConversionOptions(output_format="plain")).content)

        browser.close()



def match_files(prog):
    directory = Path('results')

    for path in directory.iterdir():
        if path.is_file():
            with open(str(path), "r", encoding="utf-8") as file:
                for word in file.read().split():
                    if prog.search(word):
                        print(word)



if __name__ == '__main__':
    urls = obtain_site_urls(SITE_URL)

    playwright_crawl(urls)

    pattern = '|'.join('(%s)' % case for case in MATCH_SPECIFICATION)
    prog = re.compile(pattern, re.I)
    match_files(prog)