#!/usr/bin/env python3
# Debug Selenium scraper filtering

import logging
from ebay_selenium_scraper import EbaySeleniumScraper

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_filtering():
    print("🔍 Debugging Selenium scraper filtering...")
    
    scraper = EbaySeleniumScraper()
    
    if not scraper.driver:
        print("❌ Failed to initialize Chrome driver")
        return
    
    try:
        # Navigate to eBay search
        search_url = "https://www.ebay.com/sch/i.html?_nkw=champion+reverse+weave&_sop=10"
        print(f"Navigating to: {search_url}")
        
        scraper.driver.get(search_url)
        
        # Wait for page to load
        import time
        time.sleep(3)
        
        # Find items
        items = scraper.driver.find_elements(scraper.driver.find_element.__globals__['By'].CSS_SELECTOR, "div[class*='s-item']")
        print(f"Found {len(items)} items")
        
        # Check first few items
        for i, item in enumerate(items[:5]):
            print(f"\n--- Item {i+1} ---")
            
            try:
                # Get title
                title_elem = item.find_element(scraper.driver.find_element.__globals__['By'].CSS_SELECTOR, "h3.s-item__title")
                title = title_elem.text.strip()
                print(f"Title: {title}")
                
                # Check Champion reverse weave filter
                title_lower = title.lower()
                has_champion = 'champion' in title_lower
                has_reverse_weave = any(kw in title_lower for kw in ['reverse weave', 'reverse-weave', 'reverseweave'])
                
                print(f"Has 'champion': {has_champion}")
                print(f"Has 'reverse weave': {has_reverse_weave}")
                
                if has_champion and has_reverse_weave:
                    print("✅ PASSES filter")
                else:
                    print("❌ FAILS filter")
                
                # Get price
                try:
                    price_elem = item.find_element(scraper.driver.find_element.__globals__['By'].CSS_SELECTOR, "span.s-item__price")
                    price = price_elem.text.strip()
                    print(f"Price: {price}")
                except:
                    print("Price: Not found")
                
                # Get link
                try:
                    link_elem = item.find_element(scraper.driver.find_element.__globals__['By'].CSS_SELECTOR, "a.s-item__link")
                    href = link_elem.get_attribute('href')
                    print(f"Link: {href[:80]}...")
                except:
                    print("Link: Not found")
                    
            except Exception as e:
                print(f"Error processing item: {e}")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
    
    finally:
        scraper.close()
        print("🔒 Chrome driver closed")

if __name__ == "__main__":
    debug_filtering()
