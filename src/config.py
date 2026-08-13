# General:
BASE_URL = "https://books.toscrape.com/" # Base website url; must include schema (https/http) and full host
SITEMAP_PATH = "/sitemap.xml" # Url path to sitemap

URL_MODE = "absolute" # 'absolute': remove query and fragment parameters; 'url': keeps them

URL_ALLOWED_SUFFIXES = ["", ".php", ".htm", ".html"] # Specify url path suffixes that are allowed to be scraped, '': URLs missing a suffix RECOMMENDATION: do not change these (use path exclusion instead)

URL_PATH_EXCLUSION_PATTERNS = [ # Excludes URL paths from getting matched; case-insensitive
    r"^/filestore/.*",
]


# Matching:
#STRIP_NON_LETTERS = True # Replace every letter of a word that is not part of the unicode letter category or a '-' before matching
LETTER_STRIP_PATTERN = r"[\W\d_^-]" # Pattern for parts of a word that get stripped before matching; default is every non-letter except '-'

MATCH_PATTERNS = [ # Patterns that words must match; case-insensitive unless pattern wrapped in '(?-i:...)'
    # German:
    r"öko",
    r"bio",
    r"umwe",
    r"achhal",
    r"neuerb",
    r"emission",
    r"eutr",
    r"ergi",
    r"strom",
    # English:
    r"green",
    r"ecolog",
    r"eco-",
    r"sustainab",
    r"renewab",
    r"environment",
    r"carbon",
    r"footprint",
    r"offset",
    r"recycl",
    r"organic",
    r"biodegrad",
    r"energ",
    r"(?-i:CO)", # Case-sensitive
    # Dutch:
    r"groen",
    r"duurza",
    r"milieu",
    r"hernieuwb",
    r"uitstoot",
    r"klima",
    r"circulair",
    r"stroom",
]

MATCH_EXCLUSION_PATTERNS = [ # Pattern that words must not match; Case-insensitive
    r"umweg",
    r"groente",
    r"energie",
    r"energy",
    r"^strom$",
    r"^stroom$",
    r"^stromed$",
]


# Multithreading:
CONCURRENT_WORKER_THREADS = 5 # -1 for unlimited, 0 for no worker threads


# Networking:
CONCURRENT_NETWORK_REQUESTS = 20 # '-1': unlimited simultaneous network requests
MAX_NETWORK_RETRIES = 5 # Maximum retry count for a specific page
MIN_NETWORK_RETRY_DELAY = 1 # Minimum delay in seconds before next retry attempt
MAX_NETWORK_RETRY_DELAY = 20 # Maximum delay in seconds before next retry attempt
DEFAULT_NETWORK_MODE = "static" # 'static': use aiohttp (raw network requests); 'dynamic': use playwright (browser instances)


# Crawling:
SCRAPING_MODE = "static" # 'static': use aiohttp; 'dynamic': use playwright

STATIC_SCRAPE_TIMEOUT_MS = 5000 # Time in ms until aiohttp(static) timeout
DYNAMIC_SCRAPE_TIMEOUT_MS = 10000 # Time in ms until playwright(dynamic) timeout

MAX_CRAWL_DEPTH = 10


# Output:
PRINT_MODE = "csv"
CSV_PATH = "./output.csv"


# Caching:
CACHE_PATH = "./cache/" # Directory of the cache
CACHE_EXPIRY_S = 3600 # Seconds until a cached value expires; 'None': keep it forever, '0': disable caching
