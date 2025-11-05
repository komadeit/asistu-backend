"""
Browser manager for handling multiple Selenium windows
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scraper_modules.utils import get_random_user_agent
from config import HEADLESS, PAGE_LOAD_TIMEOUT, IMPLICIT_WAIT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages multiple browser windows for parallel scraping"""

    def __init__(self, num_windows=1):
        self.num_windows = num_windows
        self.drivers = []

    def create_driver(self, window_index=0):
        """Create a single Chrome driver with anti-detection settings"""
        chrome_options = Options()

        # Anti-detection settings
        if HEADLESS:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Random user agent
        user_agent = get_random_user_agent()
        chrome_options.add_argument(f'user-agent={user_agent}')

        # Window size
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")

        # Position windows differently if multiple
        if not HEADLESS and window_index > 0:
            x_position = (window_index * 100) % 800
            y_position = (window_index * 100) % 400
            chrome_options.add_argument(f"--window-position={x_position},{y_position}")

        # Create driver - Selenium 4.6+ auto-manages ChromeDriver
        # No need for webdriver_manager, Selenium handles it automatically
        driver = webdriver.Chrome(options=chrome_options)

        # Set timeouts
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        driver.implicitly_wait(IMPLICIT_WAIT)

        # Execute CDP commands to prevent detection
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.info(f"Browser window {window_index + 1} created successfully")
        return driver

    def start(self):
        """Start all browser windows"""
        logger.info(f"Starting {self.num_windows} browser window(s)...")
        for i in range(self.num_windows):
            try:
                driver = self.create_driver(window_index=i)
                self.drivers.append(driver)
            except Exception as e:
                logger.error(f"Failed to create browser window {i + 1}: {e}")
                # Clean up any created drivers
                self.cleanup()
                raise

        logger.info(f"All {self.num_windows} browser window(s) started successfully")
        return self.drivers

    def cleanup(self):
        """Close all browser windows"""
        logger.info("Closing all browser windows...")
        for i, driver in enumerate(self.drivers):
            try:
                driver.quit()
                logger.info(f"Browser window {i + 1} closed")
            except Exception as e:
                logger.error(f"Error closing browser window {i + 1}: {e}")

        self.drivers = []
        logger.info("All browser windows closed")

    def __enter__(self):
        """Context manager entry"""
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
