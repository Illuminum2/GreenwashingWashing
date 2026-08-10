import re

from sites import Site, Page



class Matcher:
    @staticmethod
    def _compile_patterns(patterns: list[str]) -> re.Pattern | None:
        pattern = '|'.join('(%s)' % case for case in patterns) # Merge patterns into one

        if pattern != '': # Empty string matches everything
            return re.compile(pattern, re.I | re.U)
        return None


    @staticmethod
    def _match_page(page: Page, match_prog: re.Pattern, anti_prog: re.Pattern | None) -> None:
        if page.content:
            for word in page.content.split():
                if match_prog.search(word) and (not anti_prog.search(word) if anti_prog else True):
                        page.matches.append(word)


    @staticmethod
    def match_site(site: Site, match_patterns: list[str], anti_match_patterns: list[str]) -> None:
        if not match_patterns:
            raise ValueError('Empty list of match patterns provided')

        match_prog = Matcher._compile_patterns(match_patterns)
        anti_prog = Matcher._compile_patterns(anti_match_patterns)

        for page in site.pages:
            Matcher._match_page(page, match_prog, anti_prog)
