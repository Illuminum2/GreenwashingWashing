import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor

from modules.crawler import Crawler
from modules.matcher import Matcher
from modules.printer import Printer

from utils.cache import Cache
from data.sites import Site
from network.url import Url

from utils.config import Config


parser = argparse.ArgumentParser(description="A script crawling a website to report every page containing a greenwashing related word. Configure match patterns in './config.toml'.")

parser.add_argument("url", type=str, help="Base website url, must include schema (https/http) and full host")
parser.add_argument("-s", "--static", action="store_true", help="Use aiohttp requests (raw network requests) for scraping")
parser.add_argument("-d", "--dynamic", action="store_true", help="Use playwright (chromium instance) for scraping")
parser.add_argument("-c", "--cache-skip", action="store_true", help="Skip cache and always make new network request")

args = parser.parse_args()


async def main():
    if not args.url:
        raise ValueError("Base url is not set")
    base_url = Url(args.url)

    mode = Config.get("crawl.default_mode", "static", passed=("dynamic" if args.dynamic else ("static" if args.static else None)))

    if args.cache_skip:
        Cache.disable()


    print(f"Scraping site '{base_url}' with mode '{mode}'{' (cache skipped)' if args.cache_skip else ''}:\n")


    site = Site(base_url)

    site.add_page(base_url)
    if Config.has("general.sitemap_path"):
        site.add_page(Url(Config.get("general.sitemap_path"), base_url))

    if Config.get("multithreading.concurrent_threads", 10) == 0:
        raise ValueError("Concurrent worker threads is set to 0, must be >1 or -1 for unlimited")

    max_workers = Config.get("multithreading.concurrent_threads")
    with ThreadPoolExecutor(max_workers=(max_workers if max_workers > 0 else None)) as executor:
        asyncio.get_running_loop().set_default_executor(executor)

        match_q = asyncio.Queue()
        print_q = asyncio.Queue()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(Crawler.run(site, match_q, mode))
            tg.create_task(Matcher.run(match_q, print_q))
            tg.create_task(Printer.run(print_q))


if __name__ == '__main__':
    asyncio.run(main())
