import asyncio
from concurrent.futures import ThreadPoolExecutor

from pipeline import Pipeline
from crawler import Crawler
from matcher import Matcher

from sites import Site, Page

from config import BASE_URL, CONCURRENT_WORKER_THREADS


async def main():
    site = Site(BASE_URL)
    site.add_page(BASE_URL)

    if CONCURRENT_WORKER_THREADS == 0:
        raise ValueError("Concurrent worker threads is set to 0, must be >1 or -1 for unlimited")

    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKER_THREADS if CONCURRENT_WORKER_THREADS and CONCURRENT_WORKER_THREADS > 0 else None) as executor:
        asyncio.get_running_loop().set_default_executor(executor)

        match_q = asyncio.Queue()
        print_q = asyncio.Queue()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(Crawler.crawl_site(site, match_q))
            tg.create_task(Matcher.match_site(match_q, print_q))
            tg.create_task(print_site(print_q))


async def print_site(in_q: asyncio.Queue) -> None:
    async with asyncio.TaskGroup() as tg:
        async for page in Pipeline.queue_drain(in_q):
            tg.create_task(print_page(page))


async def print_page(page: Page) -> None:
    if page.matches:
        print(f"Page '{page.url}': ", end="")
        print (*page.matches, sep=", ")


if __name__ == '__main__':
    asyncio.run(main())
