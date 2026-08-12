from dataclasses import dataclass, field
from typing import Final


@dataclass
class Site:
    base_url: Final[str]

    _pages: dict[str, Page] = field(default_factory=dict)

    @property
    def page_urls(self) -> list[str]:
        return self._pages.keys

    @property
    def pages(self) -> list[Page]:
        return self._page.values

    def add_page(self, url: str) -> Page | None:
        if url in self.page_urls:
            return None
        
        self._pages[url] = Page(url, self)
        return self._pages[url]


@dataclass
class Page:
    url: Final[str]
    site: Site

    raw: str | None = None
    content: str | None = None
    links: list[str] = field(default_factory=list)
    matches: list[str] = field(default_factory=list)
