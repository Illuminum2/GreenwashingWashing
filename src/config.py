# General:
BASE_URL = "https://books.toscrape.com/" # Base website url; must include schema (https/http) and full host
SITEMAP_PATH = "/sitemap.xml" # Url path to sitemap

URL_MODE = "absolute" # 'absolute': remove query and fragment parameters; 'url': keeps them

URL_PATH_EXCLUSION_PATTERNS = [ # Excludes URL paths from getting matched; case-insensitive

]


# Matching:
MATCH_PATTERNS = [ # Patterns that words must match; case-insensitive
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

MATCH_EXCLUSION_PATTERNS = [ # Pattern that words must not match; Case-insensitive
    r"umweg"
]


# Multithreading:
CONCURRENT_WORKER_THREADS = 5 # -1 for unlimited, 0 for no worker threads


# Networking:
CONCURRENT_NETWORK_REQUESTS = 20 # -1 for unlimited, 0 for no network connections
MAX_NETWORK_RETRIES = 5 # Maximum amount of network retries
MIN_NETWORK_RETRY_DELAY = 1 # Minimum delay in seconds before retry attempt
MAX_NETWORK_RETRY_DELAY = 20 # Maximum delay in seconds before retry attempt
DEFAULT_NETWORK_MODE = "static" # 'static': use aiohttp (raw network requests); 'dynamic': use playwright (browser instances)


# Scraping:
STATIC_SCRAPE_TIMEOUT_MS = 5000 # Time(ms) until aiohttp timeout
DYNAMIC_SCRAPE_TIMEOUT_MS = 10000 # Time(ms) until playwright timeout

SCRAPING_MODE = "dynamic" # 'static': use aiohttp; 'dynamic': use playwright
