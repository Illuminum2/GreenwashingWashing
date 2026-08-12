from dataclasses import dataclass, field
from typing import Final

from url import Url


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

    def add_page(self, url: Url) -> Page | None:
        if (url.is_in_base(self.base_url)) and (url not in self.page_urls):
            self._pages[url] = Page(url, self)
            return self._pages[url]


@dataclass
class Page:
    url: Final[Url]
    site: Site

    raw: str | None = None
    content: str | None = None
    links: list[Url] = field(default_factory=list)
    matches: list[str] = field(default_factory=list)
