import asyncio
from concurrent.futures import ThreadPoolExecutor

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


concurrent_instances = 5


async def main():
    site = Site(BASE_URL)

    with ThreadPoolExecutor(max_workers=concurrent_instances) as executor:
        asyncio.get_running_loop().set_default_executor(executor)

        Mapper.map_site(site)
        
        await Crawler.crawl_site(site, mode="static")

        Matcher.match_site(site, MATCH_PATTERNS, ANTI_MATCH_PATTERNS)

    for page in site.pages:
        if page.matches:
            print(f"Page '{page.url}': ", end="")
            print (*page.matches, sep=", ")


if __name__ == '__main__':
    asyncio.run(main())
