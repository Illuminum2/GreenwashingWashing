import argparse
import time
from typing import Literal, Self

from gww.network.url import Url

from gww.utils.cache import Cache
from gww.utils.config import Config


class Cli:
    def __init__(self) -> None:
        self._args = Cli._parse_args()

        if not self._args.url:
            raise ValueError("Base url is not set")

        self.base_url = Url(self._args.url)
        self.crawl_mode: Literal['static', 'dynamic'] = Config.get(
            "crawl.default_mode",
            "static",
            passed=("dynamic" if self._args.dynamic else ("static" if self._args.static else None))
        )

        self.page_count = 0
        self._start: float = 0.0


    def __enter__(self) -> Self:
        if self._args.cache_skip:
            Cache.disable()

        print(f"Scraping site '{self.base_url}' with crawl mode '{self.crawl_mode}'{' (cache skipped)' if self._args.cache_skip else ''}:\n")

        self._start = time.perf_counter()

        return self


    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        elapsed = time.perf_counter() - self._start

        if exc_type is not None:
            print(f"\nFailed after {elapsed:.1f}s")
            return

        print(f"\nCrawled {self.page_count} pages in {elapsed:.1f}s")


    @staticmethod
    def _parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="A script crawling a website to report every page containing a greenwashing related word. Configure match patterns in './config.toml'.")

        parser.add_argument("url", type=str, help="Base website url, must include schema (https/http) and full host")
        parser.add_argument("-s", "--static", action="store_true", help="Use aiohttp requests (raw network requests) for scraping")
        parser.add_argument("-d", "--dynamic", action="store_true", help="Use playwright (chromium instance) for scraping")
        parser.add_argument("-c", "--cache-skip", action="store_true", help="Skip cache and always make new network request")

        return parser.parse_args()