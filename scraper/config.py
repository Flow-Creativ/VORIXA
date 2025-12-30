import os

# Set Playwright Browsers Path to local if exists (for Render)
local_browsers_path = os.path.abspath("pw-browsers")
if os.path.exists(local_browsers_path):
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = local_browsers_path

# Selectors for Google Maps
SELECTORS = {
    "listings": '//div[contains(@class, "Nv2PK")]',
    "name": '.qBF1Pd',
    "rating": '.MW4etd',
    "reviews": '.UY7F9',
    "address_list": '.W4Efsd',
    "category": '.DkEaL',
    "website_auth": 'a[data-item-id="authority"]',
    "phone_btn": 'button[data-item-id^="phone:"]',
    "address_btn": 'button[data-item-id="address"]',
    "link": 'a',
}

# Browser Configuration
BROWSER_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

VIEWPORT = {"width": 1920, "height": 1080}
