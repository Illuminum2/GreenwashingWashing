import re

from sites import Site


def match_site(pattern_prog: re.Pattern, site: Site) -> None:
    for page in site.pages:
        for word in page.content.split():
            if pattern_prog.search(word):
                page.matches.append(word)
