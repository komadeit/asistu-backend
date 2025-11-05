"""
Utility functions for the scraper
"""
import time
import random
from fake_useragent import UserAgent
from config import MIN_DELAY, MAX_DELAY


def random_delay(min_delay=MIN_DELAY, max_delay=MAX_DELAY):
    """Wait for a random amount of time to appear more human-like"""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def get_random_user_agent():
    """Get a random user agent string"""
    ua = UserAgent()
    return ua.random


def human_like_scroll(driver, scroll_pause_time=2):
    """
    Scroll the page in a human-like manner
    Returns True if more content was loaded, False otherwise
    """
    # Get current scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Scroll down in chunks (more human-like)
    current_position = 0
    scroll_increment = random.randint(300, 600)

    while current_position < last_height:
        current_position += scroll_increment
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(random.uniform(0.5, 1.5))

    # Wait for page to load
    time.sleep(scroll_pause_time)

    # Calculate new scroll height and compare
    new_height = driver.execute_script("return document.body.scrollHeight")

    return new_height > last_height


def build_search_query(category, city, district=None):
    """Build a search query for Google Maps"""
    if district:
        return f"{category} {district} {city}"
    return f"{category} {city}"


def clean_phone_number(phone):
    """Clean and format phone number"""
    if not phone:
        return None
    # Remove common formatting characters
    cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    return cleaned if cleaned else None


def clean_rating(rating_text):
    """Extract numeric rating from text"""
    if not rating_text:
        return None
    try:
        # Extract first number from string (e.g., "4.5 stars" -> 4.5)
        import re
        match = re.search(r'(\d+\.?\d*)', rating_text)
        if match:
            return float(match.group(1))
    except:
        pass
    return None


def clean_review_count(review_text):
    """Extract review count from text"""
    if not review_text:
        return 0
    try:
        # Extract number from text like "(123 reviews)" or "123 yorumlar"
        import re
        match = re.search(r'(\d+)', review_text)
        if match:
            return int(match.group(1))
    except:
        pass
    return 0
