import requests
from bs4 import BeautifulSoup

import re

from playwright.sync_api import sync_playwright
from html_to_markdown import convert, ConversionOptions

from pathlib import Path
import timeit


siteUrl = "https://www.bluechip.at"



def crawl_sitemap(url):
    page = requests.get(url)
    xmlSoup = BeautifulSoup(page.content, features="xml")

    urls = xmlSoup.find_all('loc')
    res = []
    for url in urls:
        res.append(url.contents[0])

    return res



urls = [f"{siteUrl}/sitemap.xml"]
prog = re.compile(r"[^?]+\.xml")

sitemap = []

i = 0

while i < len(urls):
    res = crawl_sitemap(urls[i])

    for r in res:
        if not prog.match(r):
            if r not in sitemap:
                sitemap.append(r)
        elif r not in urls:
            urls.append(r)
    
    i += 1



with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    i = 0
    for url in sitemap:
        try:
            page.goto(url, wait_until="load", timeout=5000)
            print(url)
        except: # Do NOT do this
            pass

        htmlSoup = BeautifulSoup(page.content(), 'lxml')
        #texts = htmlSoup.find_all(string=True)

        with open(f"./results/{i}.html", "w", encoding="utf-8") as file:
            #file.writelines(textx)
            file.write(convert(str(htmlSoup.body), ConversionOptions(output_format="plain")).content)

        i += 1


    browser.close()



match_specification = [
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

pattern = '|'.join('(%s)' % case for case in match_specification)
#pattern = f"\\w*{pattern}\\w*" # Really bad performance
prog = re.compile(pattern, re.I)

directory = Path('results')

for path in directory.iterdir():
    if path.is_file():
        with open(str(path), "r", encoding="utf-8") as file:
            #matches = prog.findall(file.read())
            for word in file.read().split():
                if prog.search(word):
                    print(word)



#\wöko\w/gi
#\wbio\w/gi
#\wumwe\w/gi
#\wgrün\w/gi
#\wachhal\w/gi
#\wneuerb\w/gi
#\wemission\w/gi
#\weutr\w/gi
#\wCO\w/g
#\wergi\w/gi
#\wstrom\w/gi
