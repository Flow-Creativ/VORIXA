import time
import re
import csv
from playwright.sync_api import sync_playwright

def search_maps(keyword, max_results=10, headless=True):
    results = []
    seen = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"Searching for: {keyword}")
        
        # Go to Google Maps
        page.goto("https://www.google.com/maps?hl=en", timeout=60000)
        
        # Type keyword
        try:
            page.locator('input#searchboxinput').wait_for(state="visible", timeout=10000)
            page.locator('input#searchboxinput').fill(keyword)
            page.keyboard.press("Enter")
        except Exception as e:
            print(f"Error inputting search: {e}")
            return []
            
        # Wait for results feed
        try:
            page.wait_for_selector('div[role="feed"]', timeout=15000)
        except:
            print("Feed not found, trying fallback wait...")
            time.sleep(5)
        
        # Scroll loop to load items
        print("Scrolling to load results...")
        previous_count = 0
        consecutive_no_new = 0
        
        while True:
            # Scroll
            page.mouse.wheel(0, 5000)
            time.sleep(2)
            
            # Count listings
            listings = page.locator('//div[contains(@class, "Nv2PK")]').all()
            current_count = len(listings)
            
            if current_count == previous_count:
                consecutive_no_new += 1
                if consecutive_no_new > 2: # Stop after 3 same counts
                    break
            else:
                consecutive_no_new = 0
                previous_count = current_count
            
            if current_count >= max_results:
                break
                
        print(f"Loaded {len(listings)} listings. Starting extraction...")
        
        # Process Listings
        count = 0
        for listing in listings:
            if count >= max_results:
                break
                
            try:
                data = {
                    "name": "Unknown",
                    "category": "Unknown", 
                    "rating": "0",
                    "review_count": "0",
                    "address": "Unknown",
                    "phone": "Not Found",
                    "website": "Not Found",
                    "google_maps_url": "",
                    "lat": "",
                    "lng": "",
                    "has_website": False,
                    "has_phone": False
                }
                
                # --- List View Extraction (Fast) ---
                
                # Name
                try:
                    data['name'] = listing.locator('.qBF1Pd').inner_text()
                except:
                    data['name'] = listing.get_attribute('aria-label') or "Unknown"

                # Deduplication
                if data['name'] in seen:
                    continue
                seen.add(data['name'])

                # Rating & Reviews
                try:
                    role_img = listing.locator('.MW4etd')
                    if role_img.count() > 0:
                        data['rating'] = role_img.first.get_attribute('aria-label').split(" ")[0]
                except: pass
                
                try:
                    reviews_span = listing.locator('.UY7F9')
                    if reviews_span.count() > 0:
                        data['review_count'] = reviews_span.first.inner_text().replace('(', '').replace(')', '').replace(',', '')
                except: pass

                # Address (Partial usually in list)
                try:
                    address_div = listing.locator('.W4Efsd')
                    if address_div.count() > 0:
                         texts = address_div.all_inner_texts()
                         # Usually the second line is address/category
                         if len(texts) > 1:
                             data['address'] = texts[1].strip()
                except: pass
                
                # Google Maps URL
                try:
                    link = listing.locator('a').first
                    href = link.get_attribute('href')
                    data['google_maps_url'] = href
                    
                    # Lat Lng parsing
                    if href:
                        coords = re.search(r'!3d([-0-9.]+)!4d([-0-9.]+)', href)
                        if coords:
                            data['lat'] = coords.group(1)
                            data['lng'] = coords.group(2)
                except: pass
                
                # --- Detail View Extraction (Slow/Gold) ---
                # We click to get Website and Phone which are often hidden
                
                listing.click()
                time.sleep(1.5) # Wait for animation
                
                # Website
                try:
                    website_btn = page.locator('a[data-item-id="authority"]')
                    if website_btn.count() > 0:
                        data['website'] = website_btn.first.get_attribute("href")
                        data['has_website'] = True
                except: pass
                
                # Phone
                try:
                    # Phone format varies, look for buttons starting with phone:
                    phone_btn = page.locator('button[data-item-id^="phone:"]')
                    if phone_btn.count() > 0:
                        data['phone'] = phone_btn.first.get_attribute("aria-label").replace("Phone: ", "").strip()
                        data['has_phone'] = True
                except: pass
                
                # Category (often atop the title in detail or second line in list)
                try:
                    cat_btn = page.locator('.DkEaL') # Common category class
                    if cat_btn.count() > 0:
                         data['category'] = cat_btn.first.inner_text()
                except: pass
                
                # Full Address (Better from detail)
                try:
                    addr_btn = page.locator('button[data-item-id="address"]')
                    if addr_btn.count() > 0:
                        data['address'] = addr_btn.first.get_attribute("aria-label").replace("Address: ", "").strip()
                except: pass

                results.append(data)
                count += 1
                # print(f"Scraped: {data['name']}")
                
            except Exception as e:
                print(f"Error scraping item: {e}")
                
        browser.close()
        
    return results

if __name__ == "__main__":
    # Test
    print("Running test search...")
    data = search_maps("Coffee Shop Jakarta Selatan", max_results=5, headless=False)
    for item in data:
        print(item)
