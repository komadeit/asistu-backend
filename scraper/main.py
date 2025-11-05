"""
Google Maps Business Scraper
Scrapes business data from Google Maps and exports to Excel
"""
import pandas as pd
import os
from datetime import datetime
import logging
import argparse
from tqdm import tqdm
from scraper_modules.browser_manager import BrowserManager
from scraper_modules.google_maps import GoogleMapsScraper
from scraper_modules.utils import build_search_query
from config import NUM_WINDOWS, OUTPUT_DIR, EXCEL_FILE_PREFIX

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoogleMapsScraperApp:
    """Main application class for Google Maps scraping"""

    def __init__(self, num_windows=NUM_WINDOWS):
        self.num_windows = num_windows
        self.results = []

    def scrape_single_query(self, category, city, district=None):
        """
        Scrape a single category/city/district combination

        Args:
            category: Business category (e.g., "güzellik salonu")
            city: City name (required)
            district: District name (optional)

        Returns:
            List of scraped business data
        """
        search_query = build_search_query(category, city, district)
        logger.info(f"Starting scrape with query: '{search_query}'")

        all_results = []

        try:
            # Start browser(s)
            with BrowserManager(num_windows=1) as drivers:  # Start with 1 window for safety
                driver = drivers[0]
                scraper = GoogleMapsScraper(driver)

                # Perform scraping
                results = scraper.scrape(search_query, city, district)
                all_results.extend(results)

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise

        return all_results

    def export_to_excel(self, data, filename=None):
        """
        Export scraped data to Excel file

        Args:
            data: List of business dictionaries
            filename: Optional custom filename

        Returns:
            Path to the exported Excel file
        """
        if not data:
            logger.warning("No data to export")
            return None

        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{EXCEL_FILE_PREFIX}_{timestamp}.xlsx"

        filepath = os.path.join(OUTPUT_DIR, filename)

        # Create DataFrame
        df = pd.DataFrame(data)

        # Reorder columns for better readability
        column_order = [
            'name', 'category', 'rating', 'reviews_count',
            'phone', 'address', 'city', 'district',
            'website', 'google_maps_url',
            'search_category', 'search_city', 'search_district'
        ]

        # Only include columns that exist in the data
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]

        # Export to Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Businesses')

            # Auto-adjust column widths
            worksheet = writer.sheets['Businesses']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)

        logger.info(f"Data exported to: {filepath}")
        logger.info(f"Total records: {len(df)}")

        return filepath

    def run(self, category, city, district=None, output_filename=None):
        """
        Run the complete scraping workflow

        Args:
            category: Business category (e.g., "güzellik salonu", "diş kliniği")
            city: City name (required)
            district: District name (optional)
            output_filename: Optional custom output filename

        Returns:
            Path to the exported Excel file
        """
        logger.info("=" * 60)
        logger.info("GOOGLE MAPS BUSINESS SCRAPER")
        logger.info("=" * 60)
        logger.info(f"Category: {category}")
        logger.info(f"City: {city}")
        if district:
            logger.info(f"District: {district}")
        logger.info("=" * 60)

        try:
            # Scrape data
            results = self.scrape_single_query(category, city, district)

            if not results:
                logger.warning("No results found!")
                return None

            # Export to Excel
            excel_path = self.export_to_excel(results, output_filename)

            logger.info("=" * 60)
            logger.info("SCRAPING COMPLETED SUCCESSFULLY!")
            logger.info(f"Results saved to: {excel_path}")
            logger.info("=" * 60)

            return excel_path

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Scrape business data from Google Maps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape beauty salons in Istanbul
  python main.py --category "güzellik salonu" --city "Istanbul"

  # Scrape dental clinics in Kadıköy, Istanbul
  python main.py --category "diş kliniği" --city "Istanbul" --district "Kadıköy"

  # Scrape nail salons in Ankara with custom output filename
  python main.py --category "tırnak salonu" --city "Ankara" --output "ankara_salons.xlsx"

Categories:
  - güzellik salonu (beauty salon)
  - tırnak salonu (nail salon)
  - diş kliniği (dental clinic)
  - estetik kliniği (aesthetic clinic)
        """
    )

    parser.add_argument(
        '--category',
        type=str,
        required=True,
        help='Business category to search for (e.g., "güzellik salonu", "diş kliniği")'
    )

    parser.add_argument(
        '--city',
        type=str,
        required=True,
        help='City name (required) (e.g., "Istanbul", "Ankara")'
    )

    parser.add_argument(
        '--district',
        type=str,
        default=None,
        help='District/ilçe name (optional) (e.g., "Kadıköy", "Çankaya")'
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Custom output filename (optional)'
    )

    parser.add_argument(
        '--windows',
        type=int,
        default=1,
        help='Number of browser windows (default: 1, use 3-4 for parallel scraping)'
    )

    args = parser.parse_args()

    # Create and run scraper
    app = GoogleMapsScraperApp(num_windows=args.windows)
    app.run(
        category=args.category,
        city=args.city,
        district=args.district,
        output_filename=args.output
    )


if __name__ == "__main__":
    main()
