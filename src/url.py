import re
from urllib.parse import urlparse, urlsplit, urldefrag
from yarl import URL

import tld

from config import BASE_URL


class Url:
    _xml_prog: re.Pattern
    _base_url_fld: str


    def __init__(self, url: str, base: str | None = None) -> None:
        self.raw: str = url
        self.url = URL(url)

        if base is not None:
            self.setBase(base)


    def setBase(self, url: str) -> None:
        base_url= URL(url)

        self.url = URL.build(
            scheme=base_url.scheme,
            host=base_url.host,
            port=base_url.port,
            path=self.url.path,
            query=self.url.query,
            fragment=self.url.fragment
        )


    def isInBase(self) -> bool:
        if not self._base_url_fld:
            try:
                self._base_url_fld = tld.get_fld(BASE_URL, fix_protocol=True)
            except tld.exceptions.TldDomainNotFound:
                raise ValueError("Configured base url does not have a valid TLD")

        #return bool(tld.get_fld(url, fix_protocol=True, fail_silently=True) == Matcher._base_url_fld)
        return bool(self.fld == self._base_url_fld)


    def isXML(self) -> bool:
        if not self._xml_prog:
            self._xml_prog = re.compile(r"[^?#]+\.xml")

        return bool(self._xml_prog.search(self.url))
