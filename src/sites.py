from dataclasses import dataclass, field


@dataclass
class Site:
    base_url: str
    pages: list[Page] = field(default_factory=list)

    def page_urls(self) -> list[str]:
        return [page.url for page in self.pages] 

@dataclass
class Page:
    url: str
    raw: str = None
    content: str = None
    links: list[str] = field(default_factory=list)
    matches: list[str] = field(default_factory=list)
