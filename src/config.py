BASE_URL = "https://books.toscrape.com"


MATCH_PATTERNS = [
    "öko",
    "bio",
    "umwe",
    "achhal",
    "neuerb",
    "emission",
    "eutr",
    "ergi",
    "strom",
]

ANTI_MATCH_PATTERNS = [
    "umweg"
]


CONCURRENT_WORKER_THREADS = 5 # -1 for unlimited, 0 for no worker threads

CONCURRENT_NETWORK_REQUESTS = 20 # -1 for unlimited, 0 for no network connections

SITEMAP_PATH = "/sitemap.xml"

SCRAPING_MODE = "static" # static/dynamic