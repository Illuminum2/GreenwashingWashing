import re

from mapper import map_site
from crawler import dynamic_crawl, static_crawl
from matcher import match_site


BASE_URL = "https://www.bluechip.at"

MATCH_PATTERNS = [
    'öko',
    'bio',
    'umwe',
    'grün',
    'achhal',
    'neuerb',
    'emission',
    'eutr',
    'ergi',
    'strom',
]



if __name__ == '__main__':
    site = map_site(BASE_URL)

    dynamic_crawl(site)

    pattern = '|'.join('(%s)' % case for case in MATCH_PATTERNS) # Merge patterns into one
    prog = re.compile(pattern, re.I)
    match_site(prog, site)

    #[print(f"Page '{page.url}': {', '.join(map(str, page.matches))}") for page in site.pages if page.matches]

    for page in site.pages:
        if page.matches:
            print(f"Page '{page.url}': ", end="")
            print (*page.matches, sep=", ")
