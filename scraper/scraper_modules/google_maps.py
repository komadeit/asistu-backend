"""
Google Maps scraper logic - Optimized for speed with tab-based parallelism
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time
from scraper_modules.utils import (
    random_delay, human_like_scroll, clean_phone_number,
    clean_rating, clean_review_count
)
from config import (
    GOOGLE_MAPS_URL, SCROLL_PAUSE_TIME, MAX_RESULTS_PER_SEARCH,
    DETAIL_PAGE_DELAY, BATCH_SIZE, TABS_PER_WINDOW
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """Scraper for extracting business data from Google Maps - Optimized version"""

    def __init__(self, driver, browser_manager=None):
        self.driver = driver
        self.browser_manager = browser_manager
        self.wait = WebDriverWait(driver, 5)  # Reduced from 10

    def search(self, query):
        """Perform a search on Google Maps"""
        logger.info(f"Searching for: {query}")

        # Navigate to Google Maps
        self.driver.get(GOOGLE_MAPS_URL)
        random_delay(1, 2)  # Reduced delay

        try:
            # Find search box and enter query
            search_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(query)
            time.sleep(0.5)
            search_box.send_keys(Keys.RETURN)

            # Wait for results to load
            random_delay(2, 3)  # Reduced from 3-5

            logger.info("Search completed, waiting for results...")
            return True

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return False

    def scroll_results(self):
        """Scroll through the results panel to load more businesses - OPTIMIZED"""
        logger.info("Scrolling through results...")

        try:
            # Find the scrollable results panel
            results_panel = self.driver.find_element(
                By.CSS_SELECTOR,
                'div[role="feed"]'
            )

            scroll_count = 0
            max_scrolls = 50  # Limit scrolls to prevent infinite loop
            no_change_count = 0

            while scroll_count < max_scrolls and no_change_count < 3:
                # Get current number of results
                current_results = len(self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'div[role="feed"] > div > div > a'
                ))

                # Scroll to bottom of results panel
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                    results_panel
                )

                time.sleep(SCROLL_PAUSE_TIME)  # Using optimized config value
                scroll_count += 1

                # Check if new results loaded
                new_results = len(self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'div[role="feed"] > div > div > a'
                ))

                if new_results == current_results:
                    no_change_count += 1
                else:
                    no_change_count = 0
                    if scroll_count % 5 == 0:  # Log every 5 scrolls instead of every scroll
                        logger.info(f"Loaded {new_results} results so far...")

                # Check if we've reached the end
                try:
                    end_message = self.driver.find_element(
                        By.XPATH,
                        "//*[contains(text(), 'reached the end') or contains(text(), 'sonuna ulaştınız')]"
                    )
                    if end_message:
                        logger.info("Reached end of results")
                        break
                except NoSuchElementException:
                    pass

            logger.info(f"Scrolling completed after {scroll_count} scrolls. Total results: {new_results}")
            return True

        except Exception as e:
            logger.error(f"Error while scrolling: {e}")
            return False

    def extract_business_links(self):
        """Extract all business links from the results panel - PHASE 1 (FAST)"""
        logger.info("📋 PHASE 1: Extracting all business links...")

        try:
            # Find all business cards in the results
            business_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                'div[role="feed"] > div > div > a'
            )

            links = []
            for element in business_elements[:MAX_RESULTS_PER_SEARCH]:
                try:
                    link = element.get_attribute('href')
                    if link and '/maps/place/' in link:
                        links.append(link)
                except:
                    continue

            logger.info(f"✅ Found {len(links)} business links")
            return links

        except Exception as e:
            logger.error(f"Error extracting business links: {e}")
            return []

    def extract_business_details_fast(self, url, driver=None):
        """
        Extract detailed information from a business page - OPTIMIZED VERSION

        Args:
            url: Business page URL
            driver: Optional driver (for multi-tab usage)
        """
        if driver is None:
            driver = self.driver

        try:
            driver.get(url)
            time.sleep(DETAIL_PAGE_DELAY)  # Quick optimized delay

            business_data = {
                'name': None,
                'category': None,
                'address': None,
                'phone': None,
                'website': None,
                'rating': None,
                'reviews_count': 0,
                'google_maps_url': url,
                'city': None,
                'district': None
            }

            # Create a shorter wait for faster extraction
            fast_wait = WebDriverWait(driver, 3)

            # Extract business name
            try:
                name_element = fast_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
                )
                business_data['name'] = name_element.text
            except:
                # If name not found, skip this business
                return None

            # Extract category
            try:
                category_element = driver.find_element(
                    By.CSS_SELECTOR,
                    "button[jsaction*='category']"
                )
                business_data['category'] = category_element.text
            except:
                pass

            # Extract rating
            try:
                rating_element = driver.find_element(
                    By.CSS_SELECTOR,
                    "div.F7nice > span[aria-hidden='true']"
                )
                business_data['rating'] = clean_rating(rating_element.text)
            except:
                pass

            # Extract review count
            try:
                review_element = driver.find_element(
                    By.CSS_SELECTOR,
                    "div.F7nice > span > span > span[aria-label*='yorum'], div.F7nice > span > span > span[aria-label*='review']"
                )
                business_data['reviews_count'] = clean_review_count(review_element.get_attribute('aria-label'))
            except:
                pass

            # Extract address
            try:
                address_button = driver.find_element(
                    By.CSS_SELECTOR,
                    "button[data-item-id='address']"
                )
                address_text = address_button.get_attribute('aria-label')
                if address_text:
                    business_data['address'] = address_text.replace('Adres: ', '').replace('Address: ', '')
            except:
                pass

            # Extract phone
            try:
                phone_button = driver.find_element(
                    By.CSS_SELECTOR,
                    "button[data-item-id*='phone']"
                )
                phone_text = phone_button.get_attribute('aria-label')
                if phone_text:
                    business_data['phone'] = clean_phone_number(
                        phone_text.replace('Telefon: ', '').replace('Phone: ', '')
                    )
            except:
                pass

            # Extract website
            try:
                website_link = driver.find_element(
                    By.CSS_SELECTOR,
                    "a[data-item-id='authority']"
                )
                business_data['website'] = website_link.get_attribute('href')
            except:
                pass

            # Try to extract city and district from address
            if business_data['address']:
                parts = business_data['address'].split(',')
                if len(parts) >= 2:
                    last_part = parts[-1].strip()
                    business_data['city'] = last_part
                    if len(parts) >= 3:
                        business_data['district'] = parts[-2].strip()

            return business_data

        except Exception as e:
            logger.warning(f"Error extracting from {url}: {e}")
            return None

    def scrape_with_tabs(self, business_links, query, city, district=None):
        """
        PHASE 2: Extract details using multiple tabs for parallel processing

        Args:
            business_links: List of business URLs
            query: Search query
            city: City name
            district: Optional district name

        Returns:
            List of business data dictionaries
        """
        logger.info(f"⚡ PHASE 2: Extracting details using {TABS_PER_WINDOW} tabs...")

        if not self.browser_manager:
            # Fallback to single-tab mode
            logger.warning("No browser manager provided, using single-tab mode")
            return self._scrape_single_tab(business_links, query, city, district)

        results = []
        total = len(business_links)

        # Open tabs
        self.browser_manager.open_tabs(self.driver, TABS_PER_WINDOW)

        # Process in batches
        for batch_start in range(0, total, TABS_PER_WINDOW):
            batch_end = min(batch_start + TABS_PER_WINDOW, total)
            batch = business_links[batch_start:batch_end]

            logger.info(f"📦 Processing batch {batch_start//TABS_PER_WINDOW + 1} ({batch_start+1}-{batch_end}/{total})")

            # Open each URL in a different tab
            for tab_idx, url in enumerate(batch):
                self.browser_manager.switch_to_tab(self.driver, tab_idx)
                self.driver.get(url)

            # Small delay to let pages start loading
            time.sleep(DETAIL_PAGE_DELAY * 2)

            # Extract data from each tab
            for tab_idx, url in enumerate(batch):
                self.browser_manager.switch_to_tab(self.driver, tab_idx)

                business_data = self.extract_business_details_fast(url, self.driver)

                if business_data:
                    business_data['search_category'] = query
                    business_data['search_city'] = city
                    business_data['search_district'] = district
                    results.append(business_data)
                    logger.info(f"✓ {len(results)}/{total}: {business_data['name']}")

        # Clean up tabs
        self.browser_manager.close_extra_tabs(self.driver)

        logger.info(f"✅ PHASE 2 Complete: Extracted {len(results)} businesses")
        return results

    def _scrape_single_tab(self, business_links, query, city, district=None):
        """Fallback: Extract details using single tab (slower but safer)"""
        logger.info("Using single-tab fallback mode...")

        results = []
        for i, link in enumerate(business_links, 1):
            logger.info(f"Processing business {i}/{len(business_links)}")

            business_data = self.extract_business_details_fast(link)

            if business_data:
                business_data['search_category'] = query
                business_data['search_city'] = city
                business_data['search_district'] = district
                results.append(business_data)

            time.sleep(DETAIL_PAGE_DELAY)  # Minimal delay

        return results

    def scrape(self, query, city, district=None):
        """
        Main scraping method - OPTIMIZED WITH 2-PHASE APPROACH

        PHASE 1: Collect all business links (fast)
        PHASE 2: Extract details using tabs (parallel, much faster)

        Args:
            query: Search query (e.g., "güzellik salonu")
            city: City name (e.g., "Istanbul")
            district: Optional district name (e.g., "Kadıköy")

        Returns:
            List of business dictionaries
        """
        logger.info("=" * 60)
        logger.info(f"🚀 Starting OPTIMIZED scrape for: {query} in {city}" + (f", {district}" if district else ""))
        logger.info("=" * 60)

        # PHASE 1: Search and collect links (FAST)
        if not self.search(query):
            return []

        self.scroll_results()
        business_links = self.extract_business_links()

        if not business_links:
            logger.warning("No business links found")
            return []

        # PHASE 2: Extract details with tabs (PARALLEL)
        results = self.scrape_with_tabs(business_links, query, city, district)

        logger.info("=" * 60)
        logger.info(f"✅ Scraping completed. Found {len(results)}/{len(business_links)} businesses")
        logger.info("=" * 60)

        return results
