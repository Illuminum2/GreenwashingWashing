import re

from sites import Site, Page



class Matcher:
    @staticmethod
    def _compile_match_patterns(match_patterns: list[str]) -> re.Pattern:
        pattern = '|'.join('(%s)' % case for case in match_patterns) # Merge patterns into one
        return re.compile(pattern, re.I)


    @staticmethod
    def _match_page(page: Page, pattern_prog: re.Pattern) -> None:
        if page.content:
            for word in page.content.split():
                if pattern_prog.search(word):
                    page.matches.append(word)


    @staticmethod
    def match_site(site: Site, match_patterns: list[str]) -> None:
        prog = Matcher._compile_match_patterns(match_patterns)

        for page in site.pages:
            Matcher._match_page(page, prog)
