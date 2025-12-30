import argparse
from playwright.sync_api import sync_playwright
from scraper.core.maps_scraper import GoogleMapsScraper
from scraper.core.utils import export_to_csv

def main():
    parser = argparse.ArgumentParser(description="Google Maps Scraper")
    parser.add_argument("--keyword", type=str, required=True, help="Search keyword (e.g., 'Coffee Shop Jakarta')")
    parser.add_argument("--max", type=int, default=10, help="Max results to scrape")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (default: False in this script for visibility, usually True)")
    
    args = parser.parse_args()
    
    # User requested headless=True default in code, but CLI arg can override.
    # Let's default to True if not specified, but argparse 'store_true' defaults to False.
    # To follow requirements: "Gunakan ... headless=True".
    # We will control it here:
    
    use_headless = True
    if args.headless: # If user specifically passes --headless, we use it (which is True)
        use_headless = True
    
    # Wait, argparse store_true means if I pass --headless it becomes True.
    # If I don't pass it, it's False.
    # The requirement says "Optimasi Speed ... headless=True".
    # So we should probably default to True.
    # meaningful flag might be --headful or --visible to turn it OFF.
    # But let's stick to standard convention: --headless makes it headless.
    # However, for this specific request, the user wants optimasi speed.
    # Let's invert the logic or just set default to True in the class and allow override.
    
    # Actually, simplest is to pass the arg.
    # But to ensure compliance "Gunakan headless=True", I will make the default behavior headless=True 
    # unless --visible is passed.
    
    # Let's refactor args for better logic matching user constraints
    # Re-parsing not needed, just logic change.
    pass

def run():
    parser = argparse.ArgumentParser(description="Google Maps Scraper")
    parser.add_argument("-k", "--keyword", type=str, required=True, help="Search keyword")
    parser.add_argument("-m", "--max", type=int, default=10, help="Max results")
    parser.add_argument("--visible", action="store_true", help="Show browser window (not headless)")
    
    args = parser.parse_args()
    
    headless = not args.visible
    
    print(f"🚀 Starting Scraper for '{args.keyword}' (Max: {args.max})")
    if headless:
        print("   Mode: Headless (Fast) ⚡")
    else:
        print("   Mode: Visible (Debug) 👁️")

    with sync_playwright() as p:
        scraper = GoogleMapsScraper(p, headless=headless)
        
        if scraper.search(args.keyword):
            scraper.scroll_to_load(args.max)
            data = scraper.scrape(max_results=args.max)
            scraper.close()
            
            export_to_csv(data, filename="leads.csv")
            
            print("✨ Done!")
        else:
            scraper.close()
            print("❌ Search failed.")

if __name__ == "__main__":
    run()
