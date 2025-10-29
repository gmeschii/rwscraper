#!/usr/bin/env python3
# Quick test to see what eBay is returning

import logging
from ebay_scraper import EbayScraper

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_ebay():
    scraper = EbayScraper()
    
    # Test with just one search term
    test_term = "navy champion reverse weave"
    print(f"Testing eBay search for: {test_term}")
    
    listings = scraper._search_single_term(test_term, 1)  # Just 1 page
    
    print(f"\nFound {len(listings)} listings:")
    for i, listing in enumerate(listings):
        print(f"{i+1}. {listing['title']}")
        print(f"   Price: {listing['price']}")
        print(f"   URL: {listing['url']}")
        print()

if __name__ == "__main__":
    test_ebay()
