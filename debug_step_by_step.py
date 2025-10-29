#!/usr/bin/env python3
# Debug eBay scraper step by step

import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_step_by_step():
    url = "https://www.ebay.com/sch/i.html"
    params = {
        '_nkw': 'navy champion reverse weave',
        '_pgn': 1,
        '_sop': 10
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Step 1: Find items with s-item in class
    items = soup.find_all('div', class_=lambda x: x and 's-item' in x)
    print(f"Step 1: Found {len(items)} items with 's-item' in class")
    
    if items:
        print("Step 2: Analyzing first few items...")
        for i, item in enumerate(items[:3]):
            print(f"\nItem {i+1}:")
            
            # Check for listing ID
            link_elem = item.find('a', {'class': 's-item__link'})
            if link_elem:
                href = link_elem.get('href', '')
                print(f"  Link: {href[:80]}...")
                
                # Extract item ID
                import re
                id_match = re.search(r'/itm/(\d+)', href)
                if id_match:
                    listing_id = id_match.group(1)
                    print(f"  Listing ID: {listing_id}")
                else:
                    print("  No listing ID found")
            else:
                print("  No link element found")
            
            # Check for title
            title_elem = (item.find('h3', {'class': 's-item__title'}) or 
                         item.find('h3') or 
                         item.find('h2') or 
                         item.find('a', {'class': 's-item__link'}))
            if title_elem:
                title = title_elem.get_text(strip=True)
                print(f"  Title: {title[:60]}...")
            else:
                print("  No title found")
            
            # Check for price
            price_elem = (item.find('span', {'class': 's-item__price'}) or 
                         item.find('span', class_=lambda x: x and 'price' in x.lower()) or
                         item.find('span', class_=lambda x: x and 'cost' in x.lower()))
            if price_elem:
                price = price_elem.get_text(strip=True)
                print(f"  Price: {price}")
            else:
                print("  No price found")
            
            # Check if it's a real listing
            if title_elem:
                title = title_elem.get_text(strip=True)
                if "Shop on eBay" in title or "Daily Deals" in title:
                    print("  ❌ This is an ad, not a real listing")
                else:
                    print("  ✅ This looks like a real listing")
            
            # Check Champion reverse weave filter
            if title_elem:
                title = title_elem.get_text(strip=True).lower()
                has_champion = 'champion' in title
                has_reverse_weave = any(kw in title for kw in ['reverse weave', 'reverse-weave', 'reverseweave'])
                print(f"  Champion filter: {has_champion}")
                print(f"  Reverse weave filter: {has_reverse_weave}")
                if has_champion and has_reverse_weave:
                    print("  ✅ Passes Champion reverse weave filter")
                else:
                    print("  ❌ Fails Champion reverse weave filter")

if __name__ == "__main__":
    debug_step_by_step()
