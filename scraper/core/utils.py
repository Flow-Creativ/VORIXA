import csv
import os
from scraper.config import BROWSER_ARGS, USER_AGENT, VIEWPORT

def setup_browser(playwright, headless=True):
    """
    Sets up the browser with stealth settings.
    """
    browser = playwright.chromium.launch(
        headless=headless,
        args=BROWSER_ARGS
    )
    context = browser.new_context(
        viewport=VIEWPORT,
        user_agent=USER_AGENT
    )
    page = context.new_page()
    return browser, context, page

def export_to_csv(data, filename="leads.csv", output_dir="scraper/output"):
    """
    Exports the list of dictionaries to a CSV file.
    """
    if not data:
        print("No data to export.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filepath = os.path.join(output_dir, filename)
    
    # Get all unique keys from all items to ensure header is complete
    fieldnames = set()
    for item in data:
        fieldnames.update(item.keys())
    
    # Sort fieldnames for consistent output, putting important ones first
    priority_fields = ["name", "phone", "website", "rating", "review_count", "category", "address", "google_maps_url", "has_phone", "has_website", "status"]
    sorted_fieldnames = [f for f in priority_fields if f in fieldnames] + [f for f in fieldnames if f not in priority_fields]

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sorted_fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Data exported successfully to {filepath}")
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
