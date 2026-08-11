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
MAX_NETWORK_RETRIES = 5
MIN_NETWORK_RETRY_DELAY = 1 # Minimum delay in seconds before retry attempt
MAX_NETWORK_RETRY_DELAY = 20 # Maximum delay in seconds before retry attempt
DEFAULT_NETWORK_MODE = "static" # static/dynamic
STATIC_SCRAPE_TIMEOUT = 1000 # Time in ms for aiohttp timeout
DYNAMIC_SCRAPE_TIMEOUT = 10000 # Time in ms for playwright timeout

SITEMAP_PATH = "/sitemap.xml"

SCRAPING_MODE = "dynamic"
