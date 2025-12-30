from playwright.sync_api import sync_playwright
from scraper.core.maps_scraper import GoogleMapsScraper

def search_maps(keyword, max_results=10, headless=True):
    """
    Bridge function to use the new Class-based scraper from the Flask app.
    """
    results = []
    try:
        with sync_playwright() as p:
            # Initialize Scraper
            scraper = GoogleMapsScraper(p, headless=headless)
            
            # Perform Search
            found = scraper.search(keyword)
            if not found:
                scraper.close()
                return []
            
            # Scroll & Scrape
            scraper.scroll_to_load(max_results)
            results = scraper.scrape(max_results=max_results)
            
            scraper.close()
    except Exception as e:
        print(f"Scrape Error: {e}")
        
    return results
