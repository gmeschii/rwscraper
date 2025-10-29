#!/usr/bin/env python3
# Test simpler eBay search

import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_simple_search():
    url = "https://www.ebay.com/sch/i.html"
    
    # Try simpler parameters
    params = {
        '_nkw': 'champion reverse weave',
        '_pgn': 1
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Testing simple search: {params}")
    
    response = requests.get(url, params=params, headers=headers)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Try different selectors
    selectors = [
        'div.s-item',
        'li.s-item', 
        'div[class*="s-item"]',
        '.s-item',
        'div[data-view]',
        'div[data-testid]'
    ]
    
    for selector in selectors:
        items = soup.select(selector)
        print(f"Selector '{selector}': {len(items)} items")
        
        if items and len(items) > 5:  # Found actual listings
            print("Found listings! First few:")
            for i, item in enumerate(items[:3]):
                # Try to find title
                title_elem = item.find('h3') or item.find('h2') or item.find('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    print(f"  {i+1}. {title[:60]}...")
            break
    
    # Check if we got any results at all
    page_text = soup.get_text().lower()
    if 'no results found' in page_text or 'no listings found' in page_text:
        print("❌ No results found message detected")
    elif 'champion' in page_text:
        print(f"✅ Found {page_text.count('champion')} mentions of 'champion'")
    else:
        print("❌ No champion mentions found")

if __name__ == "__main__":
    test_simple_search()
