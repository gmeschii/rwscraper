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
import os
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
        
        # Resource-optimized options for Railway/Docker
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # Faster loading, less memory
        # Keep JavaScript enabled - eBay needs it for dynamic content
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--memory-pressure-off')
        
        # Stealth options
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Use headless mode in server environments (Docker, cloud platforms)
        # Set HEADLESS=false in .env to disable headless mode for local debugging
        if os.getenv('HEADLESS', 'true').lower() == 'true':
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--headless=new')  # Use new headless mode
            logger.info("Running in headless mode (server environment)")
        else:
            logger.info("Running in non-headless mode (local debugging)")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Page load strategy - don't wait for all resources to load
        chrome_options.page_load_strategy = 'eager'  # Only wait for DOM, not all resources
        
        try:
            # Try to use local chromedriver first, fall back to system PATH
            chromedriver_path = "./chromedriver"
            if not os.path.exists(chromedriver_path):
                # In Docker/cloud environments, chromedriver is in PATH
                chromedriver_path = "chromedriver"
            
            try:
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception:
                # Fall back to ChromeDriverManager if local driver fails
                logger.info("Local chromedriver not found, using ChromeDriverManager")
                import time
                # Add retry logic for resource-constrained environments
                max_retries = 3
                driver_path = None
                for attempt in range(max_retries):
                    try:
                        # Try to get ChromeDriver
                        try:
                            driver_path = ChromeDriverManager().install()
                        except Exception as e:
                            logger.warning(f"ChromeDriverManager failed (attempt {attempt + 1}/{max_retries}): {e}")
                            if attempt < max_retries - 1:
                                time.sleep(5)  # Wait before retry
                                continue
                            # Last resort: try to use system chromedriver
                            driver_path = "chromedriver"
                            logger.info("Using system chromedriver as fallback")
                        
                        # ChromeDriverManager may return wrong file (e.g., THIRD_PARTY_NOTICES.chromedriver)
                        # Find the actual chromedriver executable
                        if driver_path and os.path.isfile(driver_path) and "THIRD_PARTY" in driver_path:
                            # Wrong file returned, look in the same directory and subdirectories
                            driver_dir = os.path.dirname(driver_path)
                            possible_paths = [
                                os.path.join(driver_dir, "chromedriver"),
                                os.path.join(driver_dir, "chromedriver-linux64", "chromedriver"),
                                os.path.join(driver_dir, "chromedriver-mac-arm64", "chromedriver"),
                                os.path.join(driver_dir, "chromedriver-mac-x64", "chromedriver"),
                            ]
                            for path in possible_paths:
                                if os.path.exists(path):
                                    driver_path = path
                                    # Ensure executable permissions
                                    os.chmod(path, 0o755)
                                    break
                        elif driver_path and os.path.isdir(driver_path):
                            # Look for chromedriver in the directory
                            possible_paths = [
                                os.path.join(driver_path, "chromedriver"),
                                os.path.join(driver_path, "chromedriver-linux64", "chromedriver"),
                                os.path.join(driver_path, "chromedriver-mac-arm64", "chromedriver"),
                                os.path.join(driver_path, "chromedriver-mac-x64", "chromedriver"),
                            ]
                            for path in possible_paths:
                                if os.path.exists(path):
                                    driver_path = path
                                    # Ensure executable permissions
                                    os.chmod(path, 0o755)
                                    break
                        
                        # Try to create the driver with retries
                        if driver_path:
                            service = Service(driver_path)
                            # Add timeout and retry for Chrome startup
                            for chrome_attempt in range(3):
                                try:
                                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                                    # Set timeouts to prevent hanging
                                    self.driver.set_page_load_timeout(30)  # 30 second page load timeout
                                    self.driver.implicitly_wait(2)  # 2 second implicit wait (reduced for speed)
                                    break
                                except Exception as chrome_error:
                                    if chrome_attempt < 2:
                                        logger.warning(f"Chrome startup failed (attempt {chrome_attempt + 1}/3): {chrome_error}. Retrying...")
                                        time.sleep(3)
                                    else:
                                        raise
                        else:
                            raise Exception("Could not find chromedriver executable")
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"ChromeDriver setup failed (attempt {attempt + 1}/{max_retries}): {e}")
                            time.sleep(5)
                        else:
                            logger.error(f"Failed to initialize Chrome driver after {max_retries} attempts: {e}")
                            raise
            
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
        
        for i, search_term in enumerate(search_terms):
            logger.info(f"Searching eBay with Selenium for: {search_term}")
            
            try:
                listings = self._search_single_term_selenium(search_term, max_pages)
                all_listings.extend(listings)
                
                # Restart driver every 5 searches to prevent tab crashes (memory issues)
                if (i + 1) % 5 == 0 and (i + 1) < len(search_terms):
                    logger.info("Restarting eBay driver to prevent tab crashes")
                    self.close()
                    time.sleep(3)
                    self.setup_driver()
                    if self.driver is None:
                        logger.error("Failed to restart eBay driver")
                        break
                
                # Be respectful - add delay between searches
                time.sleep(3)
                
            except Exception as e:
                error_msg = str(e)
                # Check if it's a tab crash
                if 'tab crashed' in error_msg.lower() or 'session' in error_msg.lower():
                    logger.warning(f"Tab crashed for '{search_term}'. Restarting driver...")
                    try:
                        self.close()
                        time.sleep(3)
                        self.setup_driver()
                        if self.driver is None:
                            logger.error("Failed to restart driver after tab crash")
                            break
                        # Retry the search after restart
                        try:
                            listings = self._search_single_term_selenium(search_term, max_pages)
                            all_listings.extend(listings)
                        except Exception as retry_error:
                            logger.error(f"Retry failed for '{search_term}': {retry_error}")
                    except Exception as restart_error:
                        logger.error(f"Failed to restart driver: {restart_error}")
                        break
                else:
                    logger.error(f"Error searching for '{search_term}': {e}")
                continue
        
        logger.info(f"Found {len(all_listings)} total eBay listings with Selenium")
        return all_listings
    
    def _search_single_term_selenium(self, search_term, max_pages):
        """Search for a single term using Selenium"""
        listings = []
        
        try:
            # Check if driver is still valid
            if not self.driver:
                logger.warning("Driver is None, cannot search")
                return []
            
            # Navigate to eBay search
            search_url = f"{self.base_url}/sch/i.html?_nkw={search_term.replace(' ', '+')}&_sop=10"
            logger.info(f"Navigating to: {search_url}")
            
            try:
                self.driver.get(search_url)
            except Exception as nav_error:
                error_msg = str(nav_error).lower()
                if 'tab crashed' in error_msg or 'session' in error_msg:
                    logger.warning(f"Tab crashed during navigation for '{search_term}'")
                    raise  # Re-raise to trigger restart in search_listings
                raise
            
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
            error_msg = str(e).lower()
            if 'tab crashed' in error_msg or 'session' in error_msg:
                logger.error(f"Tab crashed in Selenium search for '{search_term}': {e}")
                raise  # Re-raise to trigger restart
            logger.error(f"Error in Selenium search for '{search_term}': {e}")
        
        return listings
    
    def _extract_listings_selenium(self, search_term):
        """Extract listings using Selenium - optimized for speed"""
        listings = []
        
        try:
            # Use JavaScript to extract all data at once (much faster than find_element)
            script = """
            var items = document.querySelectorAll('li.s-card, li[class*="s-card"], div[class*="s-item"], div.s-item, li.s-item');
            var results = [];
            var maxItems = Math.min(items.length, 50);
            
            for (var i = 0; i < maxItems; i++) {
                var item = items[i];
                try {
                    // Get link and ID
                    var link = item.querySelector('a.s-item__link, a[class*="s-item__link"], a[href*="/itm/"]');
                    if (!link) continue;
                    var href = link.getAttribute('href') || '';
                    var idMatch = href.match(/\\/itm\\/(\\d+)/);
                    if (!idMatch) continue;
                    var listingId = idMatch[1];
                    
                    // Get title
                    var titleElem = item.querySelector('.s-card__title, h3.s-item__title, h3[class*="s-item__title"], h3, h2, a.s-item__link');
                    var title = titleElem ? titleElem.textContent.trim() : '';
                    if (!title || title.includes('Shop on eBay') || title.includes('Daily Deals')) continue;
                    
                    // Get price
                    var priceElem = item.querySelector('.s-card__price, span.s-item__price, span[class*="s-item__price"], span[class*="price"]');
                    var price = priceElem ? priceElem.textContent.trim() : 'Price not available';
                    
                    // Get image
                    var imgElem = item.querySelector('img.s-item__image, img[class*="s-item__image"], img');
                    var imageUrl = '';
                    if (imgElem) {
                        imageUrl = imgElem.getAttribute('src') || imgElem.getAttribute('data-src') || '';
                        if (imageUrl.startsWith('//')) imageUrl = 'https:' + imageUrl;
                        else if (imageUrl.startsWith('/')) imageUrl = 'https://i.ebayimg.com' + imageUrl;
                    }
                    
                    results.push({
                        id: listingId,
                        title: title,
                        price: price,
                        url: href,
                        image: imageUrl
                    });
                } catch(e) {
                    continue;
                }
            }
            return results;
            """
            
            # Temporarily disable implicit wait for faster execution
            self.driver.implicitly_wait(0)
            try:
                items_data = self.driver.execute_script(script)
            finally:
                self.driver.implicitly_wait(2)  # Restore to 2 seconds
            
            if not items_data:
                logger.warning("No listing items found")
                return []
            
            logger.info(f"Extracted {len(items_data)} items via JavaScript")
            
            # Process the extracted data
            for item_data in items_data:
                try:
                    # Filter items based on search term
                    if not self._matches_search_term(item_data.get('title', '').lower(), search_term):
                        continue
                    
                    listings.append({
                        'listing_id': item_data['id'],
                        'platform': 'eBay',
                        'title': item_data['title'],
                        'price': item_data['price'],
                        'url': item_data['url'],
                        'image_url': item_data['image'],
                        'search_term': search_term
                    })
                except Exception as e:
                    logger.debug(f"Error processing item data: {e}")
                    continue
            
            logger.info(f"Found {len(listings)} listings for '{search_term}'")
                    
        except Exception as e:
            logger.error(f"Error extracting listings: {e}")
            # Fallback to slower method if JavaScript fails
            logger.info("Falling back to slower extraction method...")
            return self._extract_listings_selenium_fallback(search_term)
        
        return listings
    
    def _extract_listings_selenium_fallback(self, search_term):
        """Fallback extraction method using find_element (slower but more reliable)"""
        listings = []
        
        try:
            selectors = ["li.s-card", "li[class*='s-card']", "div[class*='s-item']", "div.s-item", "li.s-item"]
            items = []
            for selector in selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        logger.info(f"Found {len(items)} items with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not items:
                return []
            
            max_items = 50
            items_to_process = items[:max_items] if len(items) > max_items else items
            
            for item in items_to_process:
                try:
                    listing_data = self._extract_item_data_selenium(item, search_term)
                    if listing_data:
                        listings.append(listing_data)
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in fallback extraction: {e}")
        
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
                    # Use shorter timeout for element finding
                    link_elem = item.find_element(By.CSS_SELECTOR, selector)
                    href = link_elem.get_attribute('href')
                    
                    if href and '/itm/' in href:
                        # Extract item ID
                        id_match = re.search(r'/itm/(\d+)', href)
                        if id_match:
                            listing_id = id_match.group(1)
                            break
                except (NoSuchElementException, Exception):
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
                    if title and title not in ["Shop on eBay", "Daily Deals"]:
                        break
                except (NoSuchElementException, Exception):
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
                    if price_text and ('$' in price_text or 'USD' in price_text):
                        price = price_text
                        break
                except (NoSuchElementException, Exception):
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
                except (NoSuchElementException, Exception):
                    continue
            
            # Get listing URL
            listing_url = href
            
            # Filter items based on search term to ensure relevance
            if not self._matches_search_term(title, search_term):
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
    
    def _matches_search_term(self, title, search_term):
        """Check if the title matches the search term criteria"""
        title_lower = title.lower()
        search_lower = search_term.lower()
        
        # Extract key brand/product words from search term
        search_words = search_lower.split()
        
        # Define category patterns
        champion_patterns = ['champion']
        reverse_weave_patterns = ['reverse weave', 'reverse-weave', 'reverseweave']
        north_face_patterns = ['north face', 'northface']
        puffer_patterns = ['puffer', 'down jacket', 'down', 'nuptse', 'mountain jacket']
        levi_patterns = ['levi', 'levis', 'levi\'s']
        pendleton_patterns = ['pendleton']
        board_shirt_patterns = ['board shirt', 'wool shirt', 'flannel']
        loop_collar_patterns = ['loop collar', 'loop-collar']
        vintage_patterns = ['vintage', '80s', '90s', 'retro']
        usa_patterns = ['made in usa', 'made in u.s.a.', 'usa', 'u.s.a.']
        
        # Check for exclude keywords
        exclude_keywords = ['not ', 'like ', 'similar to ', ' style', 'inspired']
        if any(exclude in title_lower for exclude in exclude_keywords):
            # Check if it's a false positive (e.g., "not champion" but still relevant)
            if 'not champion' in title_lower and 'champion' not in search_lower:
                return False
        
        # Champion Reverse Weave matching
        if 'champion' in search_lower and 'reverse' in search_lower:
            has_champion = any(p in title_lower for p in champion_patterns)
            has_reverse_weave = any(p in title_lower for p in reverse_weave_patterns)
            return has_champion and has_reverse_weave
        
        # North Face matching
        if any(nf in search_lower for nf in north_face_patterns):
            has_north_face = any(p in title_lower for p in north_face_patterns)
            # If search includes puffer/down, require it
            if any(p in search_lower for p in puffer_patterns):
                has_puffer = any(p in title_lower for p in puffer_patterns)
                return has_north_face and has_puffer
            return has_north_face
        
        # Levi's matching
        if any(levi in search_lower for levi in levi_patterns):
            has_levi = any(p in title_lower for p in levi_patterns)
            # If search includes "black", require it
            if 'black' in search_lower:
                has_black = 'black' in title_lower
                if not has_black:
                    return False
            # If search includes "made in usa", require it
            if 'usa' in search_lower or 'made in' in search_lower:
                has_usa = any(p in title_lower for p in usa_patterns)
                if not has_usa:
                    return False
            return has_levi
        
        # Pendleton matching
        if any(pend in search_lower for pend in pendleton_patterns):
            has_pendleton = any(p in title_lower for p in pendleton_patterns)
            # If search includes board shirt or loop collar, prefer it
            if 'board shirt' in search_lower or 'loop collar' in search_lower:
                has_specific = any(p in title_lower for p in board_shirt_patterns + loop_collar_patterns)
                return has_pendleton and (has_specific or 'shirt' in title_lower)
            return has_pendleton
        
        # Generic matching: require at least 2 key words from search term
        # (excluding common words like "vintage", "80s", etc.)
        important_words = [w for w in search_words if w not in ['vintage', '80s', '90s', 'the', 'a', 'an', 'and', 'or']]
        if len(important_words) >= 2:
            matches = sum(1 for word in important_words if word in title_lower)
            return matches >= 2
        
        # Fallback: require at least one key word
        return any(word in title_lower for word in important_words if len(word) > 3)
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome driver closed")
