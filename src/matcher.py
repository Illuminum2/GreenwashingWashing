import re

from sites import Site, Page

from config import MATCH_PATTERNS, MATCH_EXCLUSION_PATTERNS


class Matcher:
    _xml_prog: re.Pattern

    @staticmethod
    def _compile_patterns(patterns: list[str]) -> re.Pattern | None:
        pattern = '|'.join('(%s)' % case for case in patterns) # Merge patterns into one

        if pattern != '': # Empty string matches everything
            return re.compile(pattern, re.I | re.U)
        return None


    @staticmethod
    def isXMLUrl(url: str) -> bool:
        if not hasattr(Matcher, '_xml_prog'):
            Matcher._xml_prog = re.compile(r"[^?#]+\.xml")

        return bool(re.search(Matcher._xml_prog, url))


    @staticmethod
    def _match_page(page: Page, match_prog: re.Pattern, match_exclusion_prog: re.Pattern | None) -> None:
        if page.content:
            for word in page.content.split():
                if match_prog.search(word) and (not match_exclusion_prog.search(word) if match_exclusion_prog is not None else True):
                        page.matches.append(word)


    @staticmethod
    def match_site(site: Site, match_patterns: list[str] = MATCH_PATTERNS, anti_match_patterns: list[str] = MATCH_EXCLUSION_PATTERNS) -> None:
        if not match_patterns:
            raise ValueError('Empty list of match patterns provided')

        match_prog = Matcher._compile_patterns(match_patterns)
        match_exclusion_prog = Matcher._compile_patterns(anti_match_patterns)

        for page in site.pages:
            Matcher._match_page(page, match_prog, match_exclusion_prog)
