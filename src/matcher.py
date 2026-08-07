import re

from sites import Site, Page



class Matcher:
    @staticmethod
    def _match_page(pattern_prog: re.Pattern, page: Page) -> None:
        if page.content:
            for word in page.content.split():
                if pattern_prog.search(word):
                    page.matches.append(word)

    @staticmethod
    def match_site(pattern_prog: re.Pattern, site: Site) -> None:
        for page in site.pages:
            Matcher._match_page(pattern_prog, page)
