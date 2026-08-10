import asyncio
import re

from mapper import Mapper
from crawler import Crawler
from matcher import Matcher

from sites import Site


BASE_URL = "https://books.toscrape.com"

MATCH_PATTERNS = [
    "öko",
    "bio",
    "umwe",
    "achhal",
    "neuerb",
    "emission",
    "eutr",
    "ergi",
    "strom",
]

ANTI_MATCH_PATTERNS = [
    "umweg"
]


async def main():
    site = Site(BASE_URL)
    Mapper.map_site(site)

    Matcher.match_site(site, MATCH_PATTERNS, ANTI_MATCH_PATTERNS)

    #[print(f"Page '{page.url}': {', '.join(map(str, page.matches))}") for page in site.pages if page.matches]

    for page in site.pages:
        if page.matches:
            print(f"Page '{page.url}': ", end="")
            print (*page.matches, sep=", ")


if __name__ == '__main__':
    asyncio.run(main())
