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
from config import (
    NUM_WINDOWS, OUTPUT_DIR, EXCEL_FILE_PREFIX,
    BATCH_MODE, CATEGORIES, CITIES
)

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
            # Start browser(s) with tab support
            browser_manager = BrowserManager(num_windows=self.num_windows)
            with browser_manager as drivers:
                driver = drivers[0]
                # Pass browser_manager to scraper for tab management
                scraper = GoogleMapsScraper(driver, browser_manager=browser_manager)

                # Perform scraping (uses optimized tab-based approach)
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

    def batch_run(self, categories=None, cities=None, district=None):
        """
        Run batch scraping for multiple categories and cities

        Args:
            categories: List of categories to scrape (default: CATEGORIES from config)
            cities: List of cities to scrape (default: CITIES from config)
            district: Optional district name (applies to all)

        Returns:
            List of paths to exported Excel files
        """
        if categories is None:
            categories = CATEGORIES
        if cities is None:
            cities = CITIES

        logger.info("=" * 80)
        logger.info("🚀 BATCH MODE: SCRAPING MULTIPLE CATEGORIES AND CITIES")
        logger.info("=" * 80)
        logger.info(f"Categories: {len(categories)}")
        logger.info(f"Cities: {len(cities)}")
        logger.info(f"Total combinations: {len(categories) * len(cities)}")
        logger.info("=" * 80)

        results_files = []
        total_combinations = len(categories) * len(cities)
        current = 0

        for city in cities:
            for category in categories:
                current += 1
                logger.info("")
                logger.info("=" * 80)
                logger.info(f"📍 BATCH {current}/{total_combinations}: {category} in {city}")
                logger.info("=" * 80)

                try:
                    # Generate filename with category and city
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    # Clean category name for filename
                    clean_category = category.replace(" ", "_").replace("/", "_")
                    filename = f"{clean_category}_{city}_{timestamp}.xlsx"

                    # Run scraping
                    excel_path = self.run(
                        category=category,
                        city=city,
                        district=district,
                        output_filename=filename
                    )

                    if excel_path:
                        results_files.append(excel_path)
                        logger.info(f"✅ Saved: {excel_path}")
                    else:
                        logger.warning(f"⚠️ No results for {category} in {city}")

                except Exception as e:
                    logger.error(f"❌ Failed to scrape {category} in {city}: {e}")
                    # Continue with next combination
                    continue

                # Small delay between different category/city combinations
                logger.info(f"Waiting 5 seconds before next batch...")
                import time
                time.sleep(5)

        logger.info("")
        logger.info("=" * 80)
        logger.info("🎉 BATCH SCRAPING COMPLETED!")
        logger.info("=" * 80)
        logger.info(f"Total files created: {len(results_files)}/{total_combinations}")
        logger.info(f"Success rate: {len(results_files)/total_combinations*100:.1f}%")
        logger.info("=" * 80)

        if results_files:
            logger.info("\n📁 Created files:")
            for f in results_files:
                logger.info(f"  - {f}")

        return results_files


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Scrape business data from Google Maps',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single category scraping
  python main.py --category "güzellik salonu" --city "Istanbul"
  python main.py --category "diş kliniği" --city "Istanbul" --district "Kadıköy"

  # Batch mode: Scrape all categories from config.py
  python main.py --batch --city "Istanbul"

  # Batch mode: All categories in all cities from config.py
  python main.py --batch

Categories (from config.py):
  - güzellik merkezi, güzellik salonu, beauty center
  - nail salon, nail art, tırnak salonu
  - diş kliniği, dental clinic
  - estetik kliniği, aesthetic clinic
        """
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Enable batch mode: scrape all categories from config.py'
    )

    parser.add_argument(
        '--category',
        type=str,
        default=None,
        help='Business category to search for (e.g., "güzellik salonu") - Required if not using --batch'
    )

    parser.add_argument(
        '--city',
        type=str,
        default=None,
        help='City name (e.g., "Istanbul") - Required if not using --batch with all cities'
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
        help='Custom output filename (optional, ignored in batch mode)'
    )

    parser.add_argument(
        '--windows',
        type=int,
        default=NUM_WINDOWS,
        help=f'Number of browser windows (default: {NUM_WINDOWS} from config.py)'
    )

    args = parser.parse_args()

    # Create scraper app
    app = GoogleMapsScraperApp(num_windows=args.windows)

    # Batch mode or single mode
    if args.batch:
        # Batch mode: scrape all categories
        if args.city:
            # Single city, all categories
            app.batch_run(cities=[args.city], district=args.district)
        else:
            # All cities, all categories
            app.batch_run(district=args.district)
    else:
        # Single mode: require category and city
        if not args.category or not args.city:
            parser.error("--category and --city are required when not using --batch mode")

        app.run(
            category=args.category,
            city=args.city,
            district=args.district,
            output_filename=args.output
        )


if __name__ == "__main__":
    main()
