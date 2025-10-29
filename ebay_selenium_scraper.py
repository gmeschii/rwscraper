# Alternative eBay scraper using Selenium (more reliable)
# This bypasses bot detection by using a real browser

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class EbaySeleniumScraper:
    def __init__(self):
        self.base_url = "https://www.ebay.com"
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with stealth options"""
        chrome_options = Options()
        
        # Stealth options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Faster loading
        # chrome_options.add_argument('--disable-javascript')  # Keep JS enabled for dynamic content
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Remove headless mode for better stealth (comment out for production)
        # chrome_options.add_argument('--headless')
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Use system ChromeDriver
            service = Service("./chromedriver")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Set window size to look more natural
            self.driver.set_window_size(1920, 1080)
            
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            logger.info("Make sure Chrome is installed")
            self.driver = None
    
    def search_listings(self, search_terms, max_pages=2):
        """Search eBay for listings using Selenium"""
        if not self.driver:
            logger.error("Driver not initialized")
            return []
        
        all_listings = []
        
        for search_term in search_terms:
            logger.info(f"Searching eBay with Selenium for: {search_term}")
            
            try:
                listings = self._search_single_term_selenium(search_term, max_pages)
                all_listings.extend(listings)
                
                # Be respectful - add delay between searches
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error searching for '{search_term}': {e}")
                continue
        
        logger.info(f"Found {len(all_listings)} total eBay listings with Selenium")
        return all_listings
    
    def _search_single_term_selenium(self, search_term, max_pages):
        """Search for a single term using Selenium"""
        listings = []
        
        try:
            # Navigate to eBay search
            search_url = f"{self.base_url}/sch/i.html?_nkw={search_term.replace(' ', '+')}&_sop=10"
            logger.info(f"Navigating to: {search_url}")
            
            self.driver.get(search_url)
            
            # Wait for page to load and JavaScript to execute
            time.sleep(5)
            
            # Wait for listings to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='s-item']"))
                )
            except TimeoutException:
                logger.warning("Timeout waiting for listings to load")
            
            # Check if we got redirected to a challenge page
            current_url = self.driver.current_url
            if 'challenge' in current_url or 'splashui' in current_url:
                logger.warning(f"Redirected to challenge page: {current_url}")
                return []
            
            # Try to find listings with multiple approaches
            listings = self._extract_listings_selenium(search_term)
            
            logger.info(f"Found {len(listings)} listings for '{search_term}'")
            
        except TimeoutException:
            logger.warning(f"Timeout waiting for page to load for '{search_term}'")
        except Exception as e:
            logger.error(f"Error in Selenium search for '{search_term}': {e}")
        
        return listings
    
    def _extract_listings_selenium(self, search_term):
        """Extract listings using Selenium"""
        listings = []
        
        try:
            # Try multiple selectors to find listing items
            selectors = [
                "li.s-card",  # eBay's current structure
                "li[class*='s-card']",
                "div[class*='s-item']",
                "div.s-item",
                "li.s-item",
                "div[data-view]",
                "div[data-testid]"
            ]
            
            items = []
            for selector in selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        logger.info(f"Found {len(items)} items with selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not items:
                logger.warning("No listing items found with any selector")
                return []
            
            for item in items:
                try:
                    listing_data = self._extract_item_data_selenium(item, search_term)
                    if listing_data:
                        listings.append(listing_data)
                except Exception as e:
                    logger.debug(f"Error extracting item data: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting listings: {e}")
        
        return listings
    
    def _extract_item_data_selenium(self, item, search_term):
        """Extract data from a single item using Selenium"""
        try:
            # Get listing ID from link - try multiple selectors
            listing_id = None
            link_selectors = [
                "a.s-item__link",
                "a[class*='s-item__link']",
                "a[href*='/itm/']",
                "a"
            ]
            
            for selector in link_selectors:
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, selector)
                    href = link_elem.get_attribute('href')
                    
                    if href and '/itm/' in href:
                        # Extract item ID
                        id_match = re.search(r'/itm/(\d+)', href)
                        if id_match:
                            listing_id = id_match.group(1)
                            break
                except NoSuchElementException:
                    continue
            
            if not listing_id:
                return None
            
            # Get title - try multiple selectors
            title = None
            title_selectors = [
                ".s-card__title",  # eBay's current structure
                "h3.s-item__title",
                "h3[class*='s-item__title']", 
                "h3",
                "h2",
                "a.s-item__link",
                "a[class*='s-item__link']",
                "[role='heading']"
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title:
                        break
                except NoSuchElementException:
                    continue
            
            if not title:
                return None
            
            # Skip ads
            if "Shop on eBay" in title or "Daily Deals" in title:
                return None
            
            # Get price - try multiple selectors
            price = "Price not available"
            price_selectors = [
                ".s-card__price",  # eBay's current structure
                "span.s-item__price",
                "span[class*='s-item__price']",
                "span[class*='price']",
                "span[class*='cost']",
                ".price",
                ".cost"
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = item.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_elem.text.strip()
                    if price_text and '$' in price_text:
                        price = price_text
                        break
                except NoSuchElementException:
                    continue
            
            # Get image - try multiple selectors
            image_url = ''
            img_selectors = [
                "img.s-item__image",
                "img[class*='s-item__image']",
                "img[src*='ebay']",
                "img"
            ]
            
            for selector in img_selectors:
                try:
                    img_elem = item.find_element(By.CSS_SELECTOR, selector)
                    src = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                    if src and ('http' in src or src.startswith('//')):
                        # Convert relative URLs to absolute
                        if src.startswith('//'):
                            image_url = 'https:' + src
                        elif src.startswith('/'):
                            image_url = 'https://i.ebayimg.com' + src
                        else:
                            image_url = src
                        break
                except NoSuchElementException:
                    continue
            
            # Get listing URL
            listing_url = href
            
            # Filter for Champion reverse weave items
            if not self._is_champion_reverse_weave(title):
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
            logger.debug(f"Error extracting item data: {e}")
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
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome driver closed")
