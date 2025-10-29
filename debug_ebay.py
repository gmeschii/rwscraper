#!/usr/bin/env python3
# Debug eBay scraping

import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_ebay():
    url = "https://www.ebay.com/sch/i.html"
    params = {
        '_nkw': 'navy champion reverse weave',
        '_pgn': 1,
        '_sop': 10,  # Sort by newly listed
        'LH_BIN': 1,  # Buy it now only
        'LH_Complete': 1,  # Completed listings
        'LH_Sold': 0,  # Not sold
        'rt': 'nc'  # Return completed listings
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Requesting: {url}")
    print(f"Params: {params}")
    
    response = requests.get(url, params=params, headers=headers)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for different possible selectors
    selectors_to_try = [
        'div.s-item',
        'div[class*="s-item"]',
        'li.s-item',
        'div[data-view="mi:1686|iid:1"]',
        '.s-item'
    ]
    
    for selector in selectors_to_try:
        items = soup.select(selector)
        print(f"\nSelector '{selector}': Found {len(items)} items")
        
        if items:
            print("First few items:")
            for i, item in enumerate(items[:3]):
                title_elem = item.find('h3') or item.find('h2') or item.find('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    print(f"  {i+1}. {title[:60]}...")
    
    # Also check for any items with "champion" in the text
    all_text = soup.get_text().lower()
    champion_count = all_text.count('champion')
    print(f"\nTotal 'champion' mentions in page: {champion_count}")
    
    # Save HTML for inspection
    with open('ebay_debug.html', 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    print("Saved HTML to ebay_debug.html")

if __name__ == "__main__":
    debug_ebay()
