import time
from scraper.config import SELECTORS
from scraper.core.utils import setup_browser
from scraper.core.parser import Parser

class GoogleMapsScraper:
    def __init__(self, playwright, headless=True):
        self.browser, self.context, self.page = setup_browser(playwright, headless)
        self.parser = Parser()
        self.seen_names = set()

    def close(self):
        self.browser.close()

    def search(self, keyword):
        print(f"🔍 Searching for: {keyword}")
        self.page.goto(f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}", timeout=60000)
        try:
            self.page.wait_for_selector(SELECTORS['listings'], timeout=15000)
        except:
            print("❌ No results found or timeout.")
            return False
        return True

    def scroll_to_load(self, max_results):
        print("🔄 Scrolling to load listings...")
        previous_count = 0
        consecutive_no_new = 0
        
        while True:
            self.page.mouse.wheel(0, 5000)
            time.sleep(1.5) # Slight delay
            
            listings = self.page.locator(SELECTORS['listings']).all()
            current_count = len(listings)
            
            if current_count == previous_count:
                consecutive_no_new += 1
                if consecutive_no_new > 3:
                    break
            else:
                consecutive_no_new = 0
                previous_count = current_count
                
            if current_count >= max_results:
                break
            
            print(f"   Loaded {current_count}/{max_results}...")
            
        print(f"✅ Finished scrolling. Total visible: {len(listings)}")

    def scrape(self, max_results=10):
        results = []
        listings = self.page.locator(SELECTORS['listings']).all()
        
        print(f"🚀 Starting extraction for {min(len(listings), max_results)} listings...")
        
        for i, listing in enumerate(listings[:max_results]):
            try:
                # 1. Basic Data (Fast, no click)
                data = self.parser.extract_basic_data(listing)
                
                # Dedup
                if data["name"] in self.seen_names:
                    print(f"   ⚠️ Skipping duplicate: {data['name']}")
                    continue
                self.seen_names.add(data["name"])

                # 2. Detail Data (Click required for Gold Data)
                # We click the listing to see details
                try:
                    listing.click()
                    time.sleep(1.2) # Wait for panel animation and data load
                    
                    detail_data = self.parser.extract_detail_data(self.page)
                    data.update(detail_data)
                except Exception as click_err:
                    print(f"   ⚠️ Could not click item: {click_err}")
                
                results.append(data)
                print(f"   [{i+1}] {data['name']} | 📞 {data['phone']} | 🌐 {data['has_website']}")
                
            except Exception as e:
                print(f"   ⚠️ Error scraping item {i}: {e}")
                
        return results
