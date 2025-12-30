import time
from playwright.sync_api import sync_playwright

def search_maps(keyword, max_results=10, headless=True):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        
        # Go to Google Maps
        page.goto("https://www.google.com/maps", timeout=60000)
        
        # Type keyword
        page.locator('//input[@id="searchboxinput"]').fill(keyword)
        page.keyboard.press("Enter")
        
        # Wait for results - using role="feed" is better than aria-label which depends on language
        try:
            page.wait_for_selector('div[role="feed"]', timeout=15000)
        except:
             time.sleep(5)
        
        time.sleep(3) 

        # Scroll loop
        previous_count = 0
        consecutive_no_new_results = 0
        
        while len(results) < max_results:
            # Scroll the feed
            page.eval_on_selector('div[role="feed"]', 'e => e.scrollBy(0, 1000)')
            time.sleep(2)
            
            # Find all listings currently loaded
            listings = page.locator('//div[contains(@class, "Nv2PK")]').all()
            
            # If we have enough listings in DOM, or if scrolling doesn't load more
            if len(listings) == previous_count:
                consecutive_no_new_results += 1
                if consecutive_no_new_results > 3: # Stop if no new results after 3 scrolls
                     break
            else:
                consecutive_no_new_results = 0
                previous_count = len(listings)
            
            if len(listings) >= max_results:
                break
        
        listings = page.locator('//div[contains(@class, "Nv2PK")]').all()
        print(f"Found {len(listings)} potential listings for {keyword}")
        
        count = 0
        for listing in listings:
            if count >= max_results:
                break
            try:
                # Click to get details (sometimes needed for full info, but speeding up by just grabbing visible info if possible)
                # For high volume, clicking each is slow. 
                # Optimization: Try to get info from the card itself if possible.
                # However, phone number usually requires click or is hidden.
                # For accuracy, we click.
                listing.click()
                time.sleep(1) 
                
                data = {}
                
                # Extract Name
                try:
                    data['name'] = page.locator('h1.DUwDvf').inner_text()
                except:
                    # Fallback to aria-label of the listing link
                    try:
                        data['name'] = listing.locator('a').get_attribute('aria-label')
                    except:
                         data['name'] = "Unknown"

                # Extract Phone
                try:
                    phone_locator = page.locator('button[data-item-id^="phone:"]')
                    if phone_locator.count() > 0:
                         data['phone'] = phone_locator.first.get_attribute("aria-label").replace("Phone: ", "").strip()
                    else:
                        data['phone'] = "Not Found"
                except:
                    data['phone'] = "Error"
                
                data['source'] = "Google Maps"
                results.append(data)
                count += 1
                
            except Exception as e:
                print(f"Error parsing listing: {e}")

        browser.close()
    return results

if __name__ == "__main__":
    # Test
    print(search_maps("Coffee shop Jakarta"))
