#!/usr/bin/env python3
# Test Selenium eBay scraper

import logging
from ebay_selenium_scraper import EbaySeleniumScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_selenium_ebay():
    print("🚀 Testing Selenium eBay Scraper...")
    
    scraper = EbaySeleniumScraper()
    
    if not scraper.driver:
        print("❌ Failed to initialize Chrome driver")
        print("Make sure Chrome is installed on your system")
        return
    
    try:
        # Test with just one search term
        test_term = "champion reverse weave"
        print(f"Searching for: {test_term}")
        
        listings = scraper.search_listings([test_term], max_pages=1)
        
        print(f"\n✅ Found {len(listings)} listings:")
        for i, listing in enumerate(listings[:5]):  # Show first 5
            print(f"\n{i+1}. {listing['title']}")
            print(f"   Price: {listing['price']}")
            print(f"   URL: {listing['url'][:80]}...")
            print(f"   Image: {listing['image_url'][:50]}...")
        
        if listings:
            print(f"\n🎉 Selenium scraper is working! Found {len(listings)} listings")
        else:
            print("\n⚠️  No listings found - this might be normal if there are no new listings")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        scraper.close()
        print("🔒 Chrome driver closed")

if __name__ == "__main__":
    test_selenium_ebay()
