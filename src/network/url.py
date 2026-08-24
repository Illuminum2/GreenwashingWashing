from contextlib import suppress

import tld
from yarl import URL

from utils.patterns import Patterns

from utils.config import Config


class Url:
    _path_exclusion_prog = Patterns.compile_patterns_iu(Config.get("general.url_path_exclusion_patterns"))


    @staticmethod
    def parse_url(url: str, base: Url | None = None, absolute: bool = Config.get("general.url_mode", "absolute") == "absolute") -> Url | None:
        with suppress(ValueError, TypeError):
            return Url(url, base, absolute)
        return None


    @staticmethod
    def parse_urls(urls: list[str], base: Url | None = None, absolute: bool = Config.get("general.url_mode", "absolute") == "absolute") -> list[Url]:
        return [url for raw in urls if (url := Url.parse_url(raw, base)) is not None]


    def __init__(self, url: str, base: Url | None = None, absolute: bool = Config.get("general.url_mode", "absolute") == "absolute") -> None:
        self.raw: str = url
        self._url = URL(url)

        if base is not None and not self._url.host: # Do not override base if base exists
            self.set_base(base)

        if absolute:
            self._url = self._url.with_query(None).with_fragment(None)

        self._update_vars(self._url)


    def _update_vars(self, url: URL):
        host: tld.Result | None = tld.get_tld(url.host, as_object=True, fix_protocol=True, fail_silently=True) if url.host else None

        self.subdomain = host.subdomain if host is not None else None
        self.domain = host.domain if host is not None else None
        self.tld = host.tld if host is not None else None
        self.fld = f"{host.domain}.{host.tld}" if host is not None else None

        self.scheme = url.scheme
        self.host = url.host
        self.port = url.port
        self.path = url.path
        self.suffix = url.suffix.lower()
        self.query = url.query
        self.fragment = url.fragment


    def set_base(self, base_url: Url) -> None:
        self._url = base_url._url.join(self._url)
        self._update_vars(self._url)


    def is_in_base(self, base_url: Url | str | None = Config.get("general.base_url")) -> bool:
        if base_url is None:
            return not bool(self.host) # Check if site is relative

        if not isinstance(base_url, Url):
            base_url = Url(base_url)
        
        return bool(self.fld == base_url.fld)


    @property
    def is_XML(self) -> bool:
        return self.suffix == ".xml"


    def is_valid(self, base_url: Url | str | None = Config.get("general.base_url")) -> bool:
        return (
            (self.is_in_base(base_url)) # Check if URL is in base url
            and (self.suffix in Config.get("general.url_allowed_suffixes", ["", ".php", ".htm", ".html"]) or self.is_XML) # Check file type
            and (not self._path_exclusion_prog.search(self.path)) # Exclude excluded paths
        )


    @property
    def absolute(self) -> str:
        return  self._url.with_query(None).with_fragment(None).human_repr()
    
    @property
    def url(self) -> str:
        return  self._url.human_repr()


    @property
    def string(self) -> str:
        if Config.get("general.url_mode", "absolute") == "absolute":
            return self.absolute
        return self.url


    def __str__(self) -> str:
        return self.string


    def __eq__(self, other: Url):
        if not isinstance(other, Url):
            return False
        return self.string == other.string


    def __hash__(self):
        return hash(self.string)
