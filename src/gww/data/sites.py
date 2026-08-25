from dataclasses import dataclass, field
from typing import Final, ValuesView

from gww.network.url import Url

from gww.utils.config import Config


@dataclass
class Site:
    base_url: Final[Url]

    _pages: dict[Url, Page] = field(default_factory=dict)


    @property
    def pages(self) -> ValuesView[Page]:
        return self._pages.values()


    def add_page(self, url: Url, depth: int = 0) -> Page | None:
        if url.is_valid(self.base_url) and url not in self._pages:
            max_depth = Config.get("crawl.max_recursion_depth", 10)

            if max_depth == 0:
                raise ValueError("Maximum crawl recursion depth is set to 0, must be >1 or -1 for unlimited")

            if max_depth < 0 or depth <= max_depth:
                self._pages[url] = Page(url, self, depth)
                return self._pages[url]


@dataclass
class Page:
    url: Final[Url]
    site: Site
    depth: int = 0

    raw: str | None = None
    errors: list[str] = field(default_factory=list)
    content: str | None = None
    links: list[Url] = field(default_factory=list)
    matches: list[str] = field(default_factory=list)
