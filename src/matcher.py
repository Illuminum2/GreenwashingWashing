import re

from sites import Site, Page



class Matcher:
    @staticmethod
    def _match_page(page: Page, pattern_prog: re.Pattern) -> None:
        if page.content:
            for word in page.content.split():
                if pattern_prog.search(word):
                    page.matches.append(word)


    @staticmethod
    def match_site(site: Site, match_patterns: list[str]) -> None:
        for page in site.pages:
            Matcher._match_page(page, prog)
