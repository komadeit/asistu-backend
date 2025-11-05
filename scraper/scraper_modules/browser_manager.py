"""
Browser manager for handling multiple Selenium windows and tabs
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scraper_modules.utils import get_random_user_agent
from config import HEADLESS, PAGE_LOAD_TIMEOUT, IMPLICIT_WAIT, TABS_PER_WINDOW
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages multiple browser windows and tabs for parallel scraping"""

    def __init__(self, num_windows=1, tabs_per_window=TABS_PER_WINDOW):
        self.num_windows = num_windows
        self.tabs_per_window = tabs_per_window
        self.drivers = []
        self.tab_handles = {}  # Track tab handles per driver

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

    def open_tabs(self, driver, num_tabs=None):
        """
        Open multiple tabs in a driver

        Args:
            driver: Selenium WebDriver instance
            num_tabs: Number of tabs to open (default: self.tabs_per_window)

        Returns:
            List of tab handles
        """
        if num_tabs is None:
            num_tabs = self.tabs_per_window

        # First tab already exists
        tabs = [driver.current_window_handle]

        # Open additional tabs
        for i in range(num_tabs - 1):
            driver.execute_script("window.open('');")
            time.sleep(0.3)  # Small delay to ensure tab opens

        # Get all tab handles
        tabs = driver.window_handles

        # Store for this driver
        driver_id = id(driver)
        self.tab_handles[driver_id] = tabs

        logger.info(f"Opened {len(tabs)} tabs in browser")
        return tabs

    def switch_to_tab(self, driver, tab_index):
        """
        Switch to a specific tab

        Args:
            driver: Selenium WebDriver instance
            tab_index: Index of the tab to switch to
        """
        driver_id = id(driver)
        if driver_id not in self.tab_handles:
            self.open_tabs(driver)

        tabs = self.tab_handles[driver_id]
        if 0 <= tab_index < len(tabs):
            driver.switch_to.window(tabs[tab_index])
        else:
            logger.warning(f"Tab index {tab_index} out of range")

    def close_extra_tabs(self, driver):
        """Close all tabs except the first one"""
        driver_id = id(driver)
        if driver_id in self.tab_handles:
            tabs = self.tab_handles[driver_id]
            # Close all tabs except the first
            for tab in tabs[1:]:
                try:
                    driver.switch_to.window(tab)
                    driver.close()
                except:
                    pass

            # Switch back to first tab
            driver.switch_to.window(tabs[0])
            self.tab_handles[driver_id] = [tabs[0]]

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
