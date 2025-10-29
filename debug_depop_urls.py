#!/usr/bin/env python3

from depop_selenium_scraper import DepopSeleniumScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def debug_depop_urls():
    scraper = DepopSeleniumScraper()
    
    # Test with a broader search to see what we get
    term = "champion reverse weave"
    print(f"\n=== Testing: {term} ===")
    
    search_url = f"{scraper.base_url}/search/?q={term.replace(' ', '+')}&sort=newest"
    print(f"Navigating to: {search_url}")
    scraper.driver.get(search_url)
    
    # Wait for page to load
    import time
    time.sleep(5)
    
    # Get all product links
    from selenium.webdriver.common.by import By
    items = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
    print(f"Found {len(items)} Depop product links")
    
    # Print first 5 URLs to see what we're getting
    for i, item in enumerate(items[:5]):
        href = item.get_attribute('href') or ''
        print(f"{i+1}. URL: {href}")
        if href:
            # Remove trailing slash and get the last part
            clean_href = href.rstrip('/')
            slug = clean_href.split('/')[-1]
            title = slug.replace('-', ' ').title()
            print(f"   Slug: '{slug}'")
            print(f"   Title: '{title}'")
            print(f"   Contains champion: {'champion' in title.lower()}")
            print(f"   Contains reverse: {'reverse' in title.lower()}")
            print(f"   Contains weave: {'weave' in title.lower()}")
        else:
            print("   No href found!")
        print()
    
    scraper.close()

if __name__ == "__main__":
    debug_depop_urls()
