# eBay Scraper for Champion Reverse Weave Listings
# Searches eBay for new listings and extracts relevant information

import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import quote, urljoin
import re
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class EbayScraper:
    def __init__(self):
        self.base_url = "https://www.ebay.com"
        self.search_url = "https://www.ebay.com/sch/i.html"
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_listings(self, search_terms, max_pages=3):
        """Search eBay for listings matching the given search terms"""
        all_listings = []
        
        for search_term in search_terms:
            logger.info(f"Searching eBay for: {search_term}")
            
            try:
                listings = self._search_single_term(search_term, max_pages)
                all_listings.extend(listings)
                
                # Be respectful - add delay between searches
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")
                continue
        
        logger.info(f"Found {len(all_listings)} total eBay listings")
        
        # Debug: Log first few listings if any found
        if all_listings:
            logger.info("Sample eBay listings found:")
            for i, listing in enumerate(all_listings[:3]):
                logger.info(f"  {i+1}. {listing['title'][:50]}... - {listing['price']}")
        
        return all_listings
    
    def _search_single_term(self, search_term, max_pages):
        """Search for a single term and return listings"""
        listings = []
        
        for page in range(1, max_pages + 1):
            try:
                page_listings = self._get_page_listings(search_term, page)
                listings.extend(page_listings)
                
                # If we got fewer than expected results, we might be on the last page
                if len(page_listings) < 50:  # eBay typically shows 50 items per page
                    break
                    
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                logger.error(f"Error getting page {page} for '{search_term}': {e}")
                break
        
        return listings
    
    def _get_page_listings(self, search_term, page):
        """Get listings from a specific page"""
        params = {
            '_nkw': search_term,
            '_pgn': page,
            '_sop': 10  # Sort by newly listed
        }
        
        try:
            response = self.session.get(self.search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._parse_listings(soup, search_term)
            
        except requests.RequestException as e:
            logger.error(f"Request failed for page {page}: {e}")
            return []
    
    def _parse_listings(self, soup, search_term):
        """Parse listings from the search results page"""
        listings = []
        
        # Find all listing items - eBay uses dynamic class names
        listing_items = soup.find_all('div', class_=lambda x: x and 's-item' in x)
        
        for item in listing_items:
            try:
                listing_data = self._extract_listing_data(item, search_term)
                if listing_data:
                    listings.append(listing_data)
            except Exception as e:
                logger.debug(f"Error parsing listing: {e}")
                continue
        
        return listings
    
    def _extract_listing_data(self, item, search_term):
        """Extract data from a single listing item"""
        try:
            # Get listing ID from the item
            listing_id = None
            link_elem = item.find('a', {'class': 's-item__link'})
            if link_elem:
                href = link_elem.get('href', '')
                # Extract item ID from URL
                id_match = re.search(r'/itm/(\d+)', href)
                if id_match:
                    listing_id = id_match.group(1)
            
            if not listing_id:
                return None
            
            # Get title - try multiple selectors
            title_elem = (item.find('h3', {'class': 's-item__title'}) or 
                         item.find('h3') or 
                         item.find('h2') or 
                         item.find('a', {'class': 's-item__link'}))
            title = title_elem.get_text(strip=True) if title_elem else "No title"
            
            # Skip if it's not a real listing (eBay sometimes shows ads)
            if "Shop on eBay" in title or "Daily Deals" in title:
                return None
            
            # Get price - try multiple selectors
            price_elem = (item.find('span', {'class': 's-item__price'}) or 
                         item.find('span', class_=lambda x: x and 'price' in x.lower()) or
                         item.find('span', class_=lambda x: x and 'cost' in x.lower()))
            price = price_elem.get_text(strip=True) if price_elem else "Price not available"
            
            # Get image URL
            img_elem = item.find('img', {'class': 's-item__image'})
            image_url = img_elem.get('src', '') if img_elem else ''
            
            # Convert relative URLs to absolute
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            elif image_url.startswith('/'):
                image_url = urljoin(self.base_url, image_url)
            
            # Get listing URL
            listing_url = link_elem.get('href', '') if link_elem else ''
            if listing_url.startswith('/'):
                listing_url = urljoin(self.base_url, listing_url)
            
            # Filter for Champion reverse weave items
            if not self._is_champion_reverse_weave(title):
                logger.debug(f"Filtered out: {title[:50]}... (not Champion reverse weave)")
                return None
            
            return {
                'listing_id': listing_id,
                'platform': 'eBay',
                'title': title,
                'price': price,
                'url': listing_url,
                'image_url': image_url,
                'search_term': search_term
            }
            
        except Exception as e:
            logger.debug(f"Error extracting listing data: {e}")
            return None
    
    def _is_champion_reverse_weave(self, title):
        """Check if the title indicates this is a Champion reverse weave item"""
        title_lower = title.lower()
        
        # Must contain "champion" and "reverse weave"
        champion_keywords = ['champion']
        reverse_weave_keywords = ['reverse weave', 'reverse-weave', 'reverseweave']
        
        has_champion = any(keyword in title_lower for keyword in champion_keywords)
        has_reverse_weave = any(keyword in title_lower for keyword in reverse_weave_keywords)
        
        # Additional filters to avoid irrelevant items
        exclude_keywords = ['not champion', 'like champion', 'similar to champion', 'champion style']
        has_exclude = any(keyword in title_lower for keyword in exclude_keywords)
        
        return has_champion and has_reverse_weave and not has_exclude
