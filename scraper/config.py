"""
Configuration settings for Google Maps Scraper
"""

# Scraping Settings
NUM_WINDOWS = 2  # Number of parallel browser windows (optimized: 2 for best speed/safety)
TABS_PER_WINDOW = 3  # Number of tabs per window for parallel detail extraction
HEADLESS = False  # Set to False to see browser windows
PAGE_LOAD_TIMEOUT = 30  # seconds
IMPLICIT_WAIT = 5  # seconds (reduced from 10)

# Anti-bot Settings (Optimized for speed while staying safe)
MIN_DELAY = 1  # Minimum delay between actions (seconds) - reduced from 2
MAX_DELAY = 3  # Maximum delay between actions (seconds) - reduced from 5
SCROLL_PAUSE_TIME = 1  # Time to wait after scrolling - reduced from 2
DETAIL_PAGE_DELAY = 0.5  # Quick delay for detail pages

# Output Settings
OUTPUT_DIR = "output"
EXCEL_FILE_PREFIX = "google_maps_results"

# Google Maps Settings
GOOGLE_MAPS_URL = "https://www.google.com/maps"
SEARCH_QUERY_TEMPLATE = "{category} {city} {district}"
MAX_RESULTS_PER_SEARCH = 500  # Maximum number of results to scrape per search

# Performance Settings
BATCH_SIZE = 10  # Number of businesses to process per tab batch

# ============================================================================
# BATCH SCRAPING CONFIGURATION
# ============================================================================

# Predefined categories to search (Türkçe ve İngilizce)
CATEGORIES = [
    "güzellik merkezi",
    "güzellik salonu",
    "beauty center",
    "nail salon",
    "nail art",
    "tırnak salonu",
    "diş kliniği",
    "dental clinic",
    "estetik kliniği",
    "aesthetic clinic",
]

# Cities to search (add more as needed)
CITIES = [
    "Istanbul",
    "Ankara",
    "Izmir",
    "Bursa",
    "Antalya",
]

# If True, scrape all categories in CATEGORIES list
# If False, use single category from CLI
BATCH_MODE = False  # Set to True to enable batch processing
