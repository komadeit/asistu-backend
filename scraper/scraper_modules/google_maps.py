"""
Google Maps scraper logic
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
from config import GOOGLE_MAPS_URL, SCROLL_PAUSE_TIME, MAX_RESULTS_PER_SEARCH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """Scraper for extracting business data from Google Maps"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def search(self, query):
        """Perform a search on Google Maps"""
        logger.info(f"Searching for: {query}")

        # Navigate to Google Maps
        self.driver.get(GOOGLE_MAPS_URL)
        random_delay(2, 4)

        try:
            # Find search box and enter query
            search_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(query)
            random_delay(1, 2)
            search_box.send_keys(Keys.RETURN)

            # Wait for results to load
            random_delay(3, 5)

            logger.info("Search completed, waiting for results...")
            return True

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return False

    def scroll_results(self):
        """Scroll through the results panel to load more businesses"""
        logger.info("Scrolling through results...")

        try:
            # Find the scrollable results panel
            # Google Maps uses a div with specific attributes for the results panel
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

                time.sleep(SCROLL_PAUSE_TIME)
                scroll_count += 1

                # Check if new results loaded
                new_results = len(self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'div[role="feed"] > div > div > a'
                ))

                if new_results == current_results:
                    no_change_count += 1
                    logger.info(f"No new results after scroll {scroll_count}")
                else:
                    no_change_count = 0
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

            logger.info(f"Scrolling completed after {scroll_count} scrolls")
            return True

        except Exception as e:
            logger.error(f"Error while scrolling: {e}")
            return False

    def extract_business_links(self):
        """Extract all business links from the results panel"""
        logger.info("Extracting business links...")

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

            logger.info(f"Found {len(links)} business links")
            return links

        except Exception as e:
            logger.error(f"Error extracting business links: {e}")
            return []

    def extract_business_details(self, url):
        """Extract detailed information from a business page"""
        try:
            self.driver.get(url)
            random_delay(2, 4)

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

            # Extract business name
            try:
                name_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
                )
                business_data['name'] = name_element.text
            except:
                logger.warning(f"Could not extract name from {url}")

            # Extract category
            try:
                category_element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "button[jsaction*='category']"
                )
                business_data['category'] = category_element.text
            except:
                pass

            # Extract rating
            try:
                rating_element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "div.F7nice > span[aria-hidden='true']"
                )
                business_data['rating'] = clean_rating(rating_element.text)
            except:
                pass

            # Extract review count
            try:
                review_element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "div.F7nice > span > span > span[aria-label*='yorum'], div.F7nice > span > span > span[aria-label*='review']"
                )
                business_data['reviews_count'] = clean_review_count(review_element.get_attribute('aria-label'))
            except:
                pass

            # Extract address
            try:
                address_button = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "button[data-item-id='address']"
                )
                address_text = address_button.get_attribute('aria-label')
                if address_text:
                    # Remove "Adres: " or "Address: " prefix
                    business_data['address'] = address_text.replace('Adres: ', '').replace('Address: ', '')
            except:
                pass

            # Extract phone
            try:
                phone_button = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "button[data-item-id*='phone']"
                )
                phone_text = phone_button.get_attribute('aria-label')
                if phone_text:
                    # Remove "Telefon: " or "Phone: " prefix
                    business_data['phone'] = clean_phone_number(
                        phone_text.replace('Telefon: ', '').replace('Phone: ', '')
                    )
            except:
                pass

            # Extract website
            try:
                website_link = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "a[data-item-id='authority']"
                )
                business_data['website'] = website_link.get_attribute('href')
            except:
                pass

            # Try to extract city and district from address
            if business_data['address']:
                # Turkish address format typically: Street, District/City
                parts = business_data['address'].split(',')
                if len(parts) >= 2:
                    # Last part usually contains city
                    last_part = parts[-1].strip()
                    business_data['city'] = last_part
                    # Second to last might be district
                    if len(parts) >= 3:
                        business_data['district'] = parts[-2].strip()

            logger.info(f"Extracted: {business_data['name']}")
            return business_data

        except Exception as e:
            logger.error(f"Error extracting business details from {url}: {e}")
            return None

    def scrape(self, query, city, district=None):
        """
        Main scraping method

        Args:
            query: Search query (e.g., "güzellik salonu")
            city: City name (e.g., "Istanbul")
            district: Optional district name (e.g., "Kadıköy")

        Returns:
            List of business dictionaries
        """
        logger.info(f"Starting scrape for: {query} in {city}" + (f", {district}" if district else ""))

        # Perform search
        if not self.search(query):
            return []

        # Scroll to load all results
        self.scroll_results()

        # Extract all business links
        business_links = self.extract_business_links()

        if not business_links:
            logger.warning("No business links found")
            return []

        # Extract details from each business
        results = []
        for i, link in enumerate(business_links, 1):
            logger.info(f"Processing business {i}/{len(business_links)}")

            business_data = self.extract_business_details(link)

            if business_data:
                # Add search parameters
                business_data['search_category'] = query
                business_data['search_city'] = city
                business_data['search_district'] = district
                results.append(business_data)

            random_delay()  # Anti-bot delay between businesses

        logger.info(f"Scraping completed. Found {len(results)} businesses")
        return results
