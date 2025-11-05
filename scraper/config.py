"""
Configuration settings for Google Maps Scraper
"""

# Scraping Settings
NUM_WINDOWS = 3  # Number of parallel browser windows (set to 1 if rate limited)
HEADLESS = False  # Set to False to see browser windows
PAGE_LOAD_TIMEOUT = 30  # seconds
IMPLICIT_WAIT = 10  # seconds

# Anti-bot Settings
MIN_DELAY = 2  # Minimum delay between actions (seconds)
MAX_DELAY = 5  # Maximum delay between actions (seconds)
SCROLL_PAUSE_TIME = 2  # Time to wait after scrolling

# Output Settings
OUTPUT_DIR = "output"
EXCEL_FILE_PREFIX = "google_maps_results"

# Google Maps Settings
GOOGLE_MAPS_URL = "https://www.google.com/maps"
SEARCH_QUERY_TEMPLATE = "{category} {city} {district}"
MAX_RESULTS_PER_SEARCH = 500  # Maximum number of results to scrape per search
