import asyncio
import re

from mapper import map_site
from crawler import crawl_site
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



async def main():
    site = map_site(BASE_URL)
    
    await crawl_site(site, mode="static")

    pattern = '|'.join('(%s)' % case for case in MATCH_PATTERNS) # Merge patterns into one
    prog = re.compile(pattern, re.I)
    match_site(prog, site)

    #[print(f"Page '{page.url}': {', '.join(map(str, page.matches))}") for page in site.pages if page.matches]

    for page in site.pages:
        if page.matches:
            print(f"Page '{page.url}': ", end="")
            print (*page.matches, sep=", ")


if __name__ == '__main__':
    asyncio.run(main())
