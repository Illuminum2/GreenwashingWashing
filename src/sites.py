from dataclasses import dataclass, field
from typing import Final

from url import Url

from config import MAX_CRAWL_DEPTH


@dataclass
class Site:
    base_url: Final[Url]

    _pages: dict[Url, Page] = field(default_factory=dict)

    @property
    def page_urls(self) -> list[Url]:
        return self._pages.keys()

    @property
    def pages(self) -> list[Page]:
        return self._pages.values()

    def add_page(self, url: Url, depth: int = 0) -> Page | None:
        if (url.is_in_base(self.base_url)) and (url not in self.page_urls) and (depth <= MAX_CRAWL_DEPTH):
            self._pages[url] = Page(url, self, depth)
            return self._pages[url]


@dataclass
class Page:
    url: Final[Url]
    site: Site
    depth: int = 0

    raw: str | None = None
    error: str | None = None
    content: str | None = None
    links: list[Url] = field(default_factory=list)
    matches: list[str] = field(default_factory=list)
