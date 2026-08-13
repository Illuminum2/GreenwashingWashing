import asyncio
from concurrent.futures import ThreadPoolExecutor

from crawler import Crawler
from matcher import Matcher
from printer import get_printer

from sites import Site
from url import Url

from config import BASE_URL, SITEMAP_PATH, CONCURRENT_WORKER_THREADS


async def main():
    site = Site(Url(BASE_URL))

    site.add_page(Url(BASE_URL))
    site.add_page(Url(SITEMAP_PATH, Url(BASE_URL)))

    if CONCURRENT_WORKER_THREADS == 0:
        raise ValueError("Concurrent worker threads is set to 0, must be >1 or -1 for unlimited")

    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKER_THREADS if CONCURRENT_WORKER_THREADS and CONCURRENT_WORKER_THREADS > 0 else None) as executor:
        asyncio.get_running_loop().set_default_executor(executor)

        match_q = asyncio.Queue()
        print_q = asyncio.Queue()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(Crawler.run(site, match_q))
            tg.create_task(Matcher.run(match_q, print_q))
            tg.create_task(get_printer().run(print_q))


if __name__ == '__main__':
    asyncio.run(main())
