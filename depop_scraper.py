# Depop Scraper for Champion Reverse Weave Listings
# Searches Depop for new listings and extracts relevant information

import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import quote, urljoin
import re
from fake_useragent import UserAgent
import json

logger = logging.getLogger(__name__)

class DepopScraper:
    def __init__(self):
        self.base_url = "https://www.depop.com"
        self.search_url = "https://www.depop.com/search"
        self.api_url = "https://webapi.depop.com/api/v1/search/products"
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Set headers to mimic a real browser more convincingly
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def search_listings(self, search_terms, max_pages=2):
        """Search Depop for listings matching the given search terms"""
        all_listings = []
        
        for search_term in search_terms:
            logger.info(f"Searching Depop for: {search_term}")
            
            try:
                listings = self._search_single_term(search_term, max_pages)
                all_listings.extend(listings)
                
                # Be respectful - add delay between searches
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")
                continue
        
        logger.info(f"Found {len(all_listings)} total Depop listings")
        return all_listings
    
    def _search_single_term(self, search_term, max_pages):
        """Search for a single term and return listings"""
        listings = []
        
        for page in range(1, max_pages + 1):
            try:
                page_listings = self._get_page_listings(search_term, page)
                listings.extend(page_listings)
                
                # If we got fewer than expected results, we might be on the last page
                if len(page_listings) < 20:  # Depop typically shows 20 items per page
                    break
                    
                time.sleep(2)  # Be respectful
                
            except Exception as e:
                logger.error(f"Error getting page {page} for '{search_term}': {e}")
                break
        
        return listings
    
    def _get_page_listings(self, search_term, page):
        """Get listings from a specific page using Depop's API"""
        params = {
            'query': search_term,
            'page': page,
            'limit': 20,
            'sort': 'newest'  # Sort by newest first
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_api_response(data, search_term)
            
        except requests.RequestException as e:
            logger.error(f"API request failed for page {page}: {e}")
            # Fallback to web scraping if API fails
            return self._fallback_web_scrape(search_term, page)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for page {page}: {e}")
            return self._fallback_web_scrape(search_term, page)
    
    def _parse_api_response(self, data, search_term):
        """Parse listings from the API response"""
        listings = []
        
        try:
            products = data.get('products', [])
            
            for product in products:
                try:
                    listing_data = self._extract_product_data(product, search_term)
                    if listing_data:
                        listings.append(listing_data)
                except Exception as e:
                    logger.debug(f"Error parsing product: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
        
        return listings
    
    def _extract_product_data(self, product, search_term):
        """Extract data from a single product"""
        try:
            # Get product ID
            product_id = str(product.get('id', ''))
            if not product_id:
                return None
            
            # Get title
            title = product.get('title', 'No title')
            
            # Get price
            price_info = product.get('price', {})
            price_amount = price_info.get('amount', 0)
            price_currency = price_info.get('currency', 'USD')
            price = f"${price_amount}" if price_currency == 'USD' else f"{price_amount} {price_currency}"
            
            # Get image URL
            images = product.get('images', [])
            image_url = images[0].get('url', '') if images else ''
            
            # Get product URL
            product_url = f"{self.base_url}/products/{product.get('slug', '')}"
            
            # Filter for Champion reverse weave items
            if not self._is_champion_reverse_weave(title):
                return None
            
            return {
                'listing_id': product_id,
                'platform': 'Depop',
                'title': title,
                'price': price,
                'url': product_url,
                'image_url': image_url,
                'search_term': search_term
            }
            
        except Exception as e:
            logger.debug(f"Error extracting product data: {e}")
            return None
    
    def _fallback_web_scrape(self, search_term, page):
        """Fallback to web scraping if API fails"""
        listings = []
        
        try:
            # Try different search approaches
            search_urls = [
                f"https://www.depop.com/search/?q={search_term.replace(' ', '+')}",
                f"https://www.depop.com/search/?q={search_term.replace(' ', '%20')}",
                f"https://www.depop.com/search/?q={search_term}"
            ]
            
            for search_url in search_urls:
                try:
                    logger.info(f"Trying Depop URL: {search_url}")
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try different selectors for product cards
                        selectors = [
                            'div[data-testid="product-card"]',
                            'div[class*="product-card"]',
                            'div[class*="ProductCard"]',
                            'a[href*="/products/"]'
                        ]
                        
                        for selector in selectors:
                            cards = soup.select(selector)
                            if cards:
                                logger.info(f"Found {len(cards)} items with selector: {selector}")
                                
                                for card in cards[:10]:  # Limit to first 10
                                    try:
                                        listing_data = self._extract_card_data(card, search_term)
                                        if listing_data:
                                            listings.append(listing_data)
                                    except Exception as e:
                                        logger.debug(f"Error parsing card: {e}")
                                        continue
                                break
                        
                        if listings:
                            break
                            
                except Exception as e:
                    logger.debug(f"Failed with URL {search_url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Web scraping fallback failed: {e}")
        
        return listings
    
    def _extract_card_data(self, card, search_term):
        """Extract data from a product card"""
        try:
            # Get product link
            link_elem = card.find('a')
            if not link_elem:
                return None
            
            href = link_elem.get('href', '')
            if not href:
                return None
            
            # Extract product ID from URL
            product_id = href.split('/')[-1] if href else ''
            if not product_id:
                return None
            
            # Get title
            title_elem = card.find('h3') or card.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else "No title"
            
            # Get price
            price_elem = card.find('span', {'data-testid': 'price'})
            price = price_elem.get_text(strip=True) if price_elem else "Price not available"
            
            # Get image
            img_elem = card.find('img')
            image_url = img_elem.get('src', '') if img_elem else ''
            
            # Convert relative URLs to absolute
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            elif image_url.startswith('/'):
                image_url = urljoin(self.base_url, image_url)
            
            # Get product URL
            product_url = urljoin(self.base_url, href)
            
            # Filter for Champion reverse weave items
            if not self._is_champion_reverse_weave(title):
                return None
            
            return {
                'listing_id': product_id,
                'platform': 'Depop',
                'title': title,
                'price': price,
                'url': product_url,
                'image_url': image_url,
                'search_term': search_term
            }
            
        except Exception as e:
            logger.debug(f"Error extracting card data: {e}")
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
