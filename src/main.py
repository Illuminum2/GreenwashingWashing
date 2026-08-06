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

    for page in site.pages:
        print(f"Page '{page.url}': {page.matches}")
