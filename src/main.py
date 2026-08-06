import re


from mapper import map_site
from crawler import dynamic_crawl, static_crawl
from matcher import match_sites



SITE_URL = "https://books.toscrape.com"

MATCH_SPECIFICATION = [
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
    urls = map_site(SITE_URL)

    sites = dynamic_crawl(urls)

    pattern = '|'.join('(%s)' % case for case in MATCH_SPECIFICATION)
    prog = re.compile(pattern, re.I)
    print(match_sites(prog, sites))
