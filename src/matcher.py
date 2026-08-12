import asyncio
import re

import tld

from pipeline import Pipeline

from sites import Site, Page

from config import BASE_URL, MATCH_PATTERNS, MATCH_EXCLUSION_PATTERNS


class Matcher:
    _xml_prog: re.Pattern
    _base_url_fld: str

    @staticmethod
    def _compile_patterns(patterns: list[str]) -> re.Pattern | None:
        pattern = '|'.join('(%s)' % case for case in patterns) # Merge patterns into one

        if pattern != '': # Empty string matches everything
            return re.compile(pattern, re.I | re.U)
        return None


    @staticmethod
    def isUrlInBase(url: str) -> bool:
        if not hasattr(Matcher, '_base_url_fld'):
            try:
                Matcher._base_url_fld = tld.get_fld(BASE_URL, fix_protocol=True)
            except tld.exceptions.TldDomainNotFound:
                raise ValueError("Configured base url does not have a valid TLD")

        return bool(tld.get_fld(url, fix_protocol=True, fail_silently=True) == Matcher._base_url_fld)


    @staticmethod
    def isXMLUrl(url: str) -> bool:
        if not hasattr(Matcher, '_xml_prog'):
            Matcher._xml_prog = re.compile(r"[^?#]+\.xml")

        return bool(re.search(Matcher._xml_prog, url))


    @staticmethod
    async def match_page(page: Page, out_q: asyncio.Queue, match_prog: re.Pattern, match_exclusion_prog: re.Pattern | None) -> None:
        if page.content:
            for word in page.content.split():
                if match_prog.search(word) and (not match_exclusion_prog.search(word) if match_exclusion_prog is not None else True):
                        page.matches.append(word)

        await out_q.put(page)


    @staticmethod
    async def match_site(in_q: asyncio.Queue, out_q: asyncio.Queue, match_patterns: list[str] = MATCH_PATTERNS, anti_match_patterns: list[str] = MATCH_EXCLUSION_PATTERNS) -> None:
        if not match_patterns:
            raise ValueError('Empty list of match patterns provided')

        match_prog = Matcher._compile_patterns(match_patterns)
        match_exclusion_prog = Matcher._compile_patterns(anti_match_patterns)

        async with asyncio.TaskGroup() as tg:
            async for page in Pipeline.queue_drain(in_q):
                tg.create_task(asyncio.get_running_loop().run_in_executor(None, Matcher.match_page, page, out_q, match_prog, match_exclusion_prog))

        out_q.shutdown()
