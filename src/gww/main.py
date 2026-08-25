import asyncio
from concurrent.futures import ThreadPoolExecutor

from gww.modules.crawler import Crawler
from gww.modules.matcher import Matcher
from gww.modules.printer import Printer

from gww.utils.cli import Cli
from gww.data.sites import Site, Page
from gww.network.url import Url

from gww.utils.config import Config


async def main(cli: Cli) -> int:
    if not Config.get("match.patterns"):
        raise ValueError('Empty match patterns list provided')

    site = Site(cli.base_url)

    site.add_page(cli.base_url)
    if Config.has("general.sitemap_path"):
        site.add_page(Url(Config.get("general.sitemap_path"), cli.base_url))

    if Config.get("multithreading.concurrent_threads", 10) == 0:
        raise ValueError("Concurrent worker threads is set to 0, must be >1 or -1 for unlimited")

    max_workers = Config.get("multithreading.concurrent_threads", 10)
    with ThreadPoolExecutor(max_workers=(max_workers if max_workers > 0 else None)) as executor:
        asyncio.get_running_loop().set_default_executor(executor)

        match_q: asyncio.Queue[Page] = asyncio.Queue()
        print_q: asyncio.Queue[Page] = asyncio.Queue()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(Crawler.run(site, match_q, cli.crawl_mode))
            tg.create_task(Matcher.run(match_q, print_q))
            tg.create_task(Printer.run(print_q))

    return len(site.pages)


if __name__ == '__main__':
    with Cli() as cli:
        cli.page_count = asyncio.run(main(cli))
