import requests

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from html_to_markdown import ConversionOptions, convert

from sites import Site


def __parse_html_to_txt(html: str) -> str:
    return convert(html, ConversionOptions(output_format="plain")).content # Parse HTML to text



def dynamic_crawl(site: Site) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        browser_page = browser.new_page()

        for page in site.pages:
            try:
                browser_page.goto(page.url, wait_until="load", timeout=5000)
            except PlaywrightTimeoutError:
                pass # Pass because parts of page might still have loaded

            content_txt = __parse_html_to_txt(browser_page.content())

            page.content = content_txt

        browser.close()



def static_crawl(site: Site) -> None:
    for page in site.pages:
        request_page = requests.get(page.url)

        content_txt = __parse_html_to_txt(request_page.content)

        page.content = content_txt
