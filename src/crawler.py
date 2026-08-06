from dataclasses import dataclass
import requests


from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from html_to_markdown import ConversionOptions, convert



@dataclass
class Site:
    url: str
    content: str



def dynamic_crawl(urls):
    res = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        for url in urls:
            try:
                page.goto(url, wait_until="load", timeout=5000)
            except PlaywrightTimeoutError:
                pass # Pass because part of page might still have loaded

            content_html = page.content()
            content_txt = convert(content_html, ConversionOptions(output_format="plain")).content # Parsed text from HTML

            res.append(Site(url, content_txt))

        browser.close()

    return res



def static_crawl(urls):
    res = []

    for url in urls:
        page = requests.get(url)

        content_html = page.content()
        content_txt = convert(content_html, ConversionOptions(output_format="plain")).content # Parsed text from HTML

        res.append(Site(url, content_txt))

    return res
