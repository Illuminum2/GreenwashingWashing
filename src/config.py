BASE_URL = "https://books.toscrape.com"

MATCH_PATTERNS = [
    r"öko",
    r"bio",
    r"umwe",
    r"achhal",
    r"neuerb",
    r"emission",
    r"eutr",
    r"ergi",
    r"strom",
]

MATCH_EXCLUSION_PATTERNS = [
    r"umweg"
]

URL_PATH_EXCLUSION_PATTERNS = []

URL_PATH_SITEMAP_PATTERNS = [
    r"\.xml$" # Default sitemap exclusion pattern
]

CONCURRENT_WORKER_THREADS = 5 # -1 for unlimited, 0 for no worker threads

CONCURRENT_NETWORK_REQUESTS = 20 # -1 for unlimited, 0 for no network connections
MAX_NETWORK_RETRIES = 5
MIN_NETWORK_RETRY_DELAY = 1 # Minimum delay in seconds before retry attempt
MAX_NETWORK_RETRY_DELAY = 20 # Maximum delay in seconds before retry attempt
DEFAULT_NETWORK_MODE = "static" # static/dynamic
STATIC_SCRAPE_TIMEOUT = 5000 # Time in ms for aiohttp timeout
DYNAMIC_SCRAPE_TIMEOUT = 10000 # Time in ms for playwright timeout

SITEMAP_PATH = "/sitemap.xml"

MAPPING_MODE = "static"

SCRAPING_MODE = "dynamic"
