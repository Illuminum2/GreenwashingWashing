import asyncio
from concurrent.futures import ThreadPoolExecutor

from mapper import Mapper
from crawler import Crawler
from matcher import Matcher

from sites import Site

from config import BASE_URL, CONCURRENT_WORKER_THREADS


async def main():
    site = Site(BASE_URL)

    if CONCURRENT_WORKER_THREADS == 0:
        raise ValueError("Concurrent worker threads is set to 0, must be >1 or -1 for unlimited")

    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKER_THREADS if CONCURRENT_WORKER_THREADS and CONCURRENT_WORKER_THREADS > 0 else None) as executor:
        asyncio.get_running_loop().set_default_executor(executor)

        await Mapper.map_site(site)
        await Crawler.crawl_site(site)
        Matcher.match_site(site)
    
    for page in site.pages:
        if page.matches:
            print(f"Page '{page.url}': ", end="")
            print (*page.matches, sep=", ")


if __name__ == '__main__':
    asyncio.run(main())
