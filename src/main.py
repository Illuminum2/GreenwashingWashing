import asyncio
import re

from mapper import Mapper
from crawler import Crawler
from matcher import Matcher


BASE_URL = "https://books.toscrape.com"

MATCH_PATTERNS = [
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


async def main():
    site = Mapper.map_site(BASE_URL)
    
    await Crawler.crawl_site(site, mode="static")

    pattern = '|'.join('(%s)' % case for case in MATCH_PATTERNS) # Merge patterns into one
    prog = re.compile(pattern, re.I)
    Matcher.match_site(prog, site)

    #[print(f"Page '{page.url}': {', '.join(map(str, page.matches))}") for page in site.pages if page.matches]

    for page in site.pages:
        if page.matches:
            print(f"Page '{page.url}': ", end="")
            print (*page.matches, sep=", ")


if __name__ == '__main__':
    asyncio.run(main())
