from urllib.parse import urlparse, urlsplit, urldefrag
from yarl import URL

import tld

from config import BASE_URL


class Url:
    _base_url_fld: str | None = None


    def __init__(self, url: str, base: str | None = None, absolute: bool = False) -> None:
        self.raw: str = url
        self._url = URL(url)

        if base is not None:
            self.set_base(base)

        if absolute:
            self._url = self._url.with_query(None).with_fragment(None)

        self._update_vars(self._url)


    def _update_vars(self, url: URL):
        host: tld.Result = tld.get_tld(url.host, as_object=True, fix_protocol=True, fail_silently=True)

        self.subdomain = host.subdomain if host is not None else None
        self.domain = host.domain if host is not None else None
        self.tld = host.tld if host is not None else None
        self.fld = f"{host.domain}.{host.tld}" if host is not None else None

        self.scheme = url.scheme
        self.host = url.host
        self.port = url.port
        self.path = url.path
        self.query = url.query
        self.fragment = url.fragment


    def set_base(self, base_url: str) -> None:
        url= URL(base_url)

        self._url = url.join(self._url)
        self._update_vars(self._url)


    @property
    def is_in_base(self) -> bool:
        if self._base_url_fld is None:
            try:
                self._base_url_fld = tld.get_fld(BASE_URL, fix_protocol=True)
            except tld.exceptions.TldDomainNotFound:
                raise ValueError("Configured base url does not have a valid TLD")

        return bool(self.fld == self._base_url_fld)


    @property
    def is_XML(self) -> bool:
        return bool(self._url.suffix is None or self._url.suffix == ".xml")


    def __str__(self):
        return self._url.human_repr()
