import re
from scraper.config import SELECTORS

class Parser:
    @staticmethod
    def extract_basic_data(listing_locator):
        """
        Extracts data visible in the list view without clicking.
        """
        data = {
            "name": "",
            "rating": "0",
            "review_count": "0",
            "address": "",
            "google_maps_url": "",
            "lat": "",
            "lng": "",
            "category": ""
        }
        
        # Name
        try:
            data["name"] = listing_locator.locator(SELECTORS["name"]).inner_text()
        except:
            data["name"] = listing_locator.get_attribute("aria-label") or ""

        # Rating
        try:
            val = listing_locator.locator(SELECTORS["rating"]).first.get_attribute("aria-label")
            if val:
                data["rating"] = val.split(" ")[0]
        except: pass

        # Reviews
        try:
            val = listing_locator.locator(SELECTORS["reviews"]).first.inner_text()
            if val:
                data["review_count"] = val.replace("(", "").replace(")", "").replace(",", "")
        except: pass

        # Address (Partial - often in list view)
        try:
            texts = listing_locator.locator(SELECTORS["address_list"]).all_inner_texts()
            # Usually the second line is address/category. Heuristics vary.
            if len(texts) > 1:
                data["address"] = texts[1].strip()
        except: pass

        # URL & Coords
        try:
            link = listing_locator.locator(SELECTORS["link"]).first
            href = link.get_attribute("href")
            data["google_maps_url"] = href
            
            if href:
                coords = re.search(r'!3d([-0-9.]+)!4d([-0-9.]+)', href)
                if coords:
                    data["lat"] = coords.group(1)
                    data["lng"] = coords.group(2)
        except: pass

        return data

    @staticmethod
    def extract_detail_data(page):
        """
        Extracts data from the detail panel (after clicking).
        """
        data = {
            "website": "Not Found",
            "has_website": False,
            "phone": "Not Found",
            "has_phone": False,
            # "address": "", # We can overwrite partial address with full address if found
        }

        # Website
        try:
            website_btn = page.locator(SELECTORS["website_auth"]).first
            if website_btn.count() > 0:
                data["website"] = website_btn.get_attribute("href")
                data["has_website"] = True
        except: pass

        # Phone
        try:
            # Look for button that starts with "phone:" in data-item-id
            phone_btn = page.locator(SELECTORS["phone_btn"]).first
            if phone_btn.count() > 0:
                data["phone"] = phone_btn.get_attribute("aria-label").replace("Phone: ", "").strip()
                data["has_phone"] = True
        except: pass

        # Improved Category Extraction (often clearer in Detail view)
        try:
            cat = page.locator(SELECTORS["category"]).first
            if cat.count() > 0:
                data["category"] = cat.inner_text()
        except: pass

        # Full Address from Detail view (usually more accurate)
        try:
            addr = page.locator(SELECTORS["address_btn"]).first
            if addr.count() > 0:
                 data["address"] = addr.get_attribute("aria-label").replace("Address: ", "").strip()
        except: pass

        return data
