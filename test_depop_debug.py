#!/usr/bin/env python3

from depop_selenium_scraper import DepopSeleniumScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_depop():
    scraper = DepopSeleniumScraper()
    
    # Test with a broader search to see what we get
    test_terms = ["champion reverse weave", "vintage champion"]
    
    for term in test_terms:
        print(f"\n=== Testing: {term} ===")
        results = scraper._search_term(term, max_pages=1, limit=5)
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"{i}. Title: {result['title']}")
            print(f"   Price: {result['price']}")
            print(f"   URL: {result['url']}")
            print(f"   Image: {result['image_url']}")
            print()
    
    scraper.close()

if __name__ == "__main__":
    test_depop()

