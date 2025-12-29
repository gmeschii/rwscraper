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

logger = logging.getLogger(__name__)

class DepopSeleniumScraper:
	def __init__(self):
		self.base_url = "https://www.depop.com"
		self.driver = None
		self.setup_driver()
	
	def setup_driver(self):
		options = Options()
		# Resource-optimized options for Railway/Docker
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		options.add_argument('--disable-gpu')
		options.add_argument('--disable-software-rasterizer')
		options.add_argument('--disable-extensions')
		options.add_argument('--disable-plugins')
		options.add_argument('--disable-images')  # Faster loading, less memory
		options.add_argument('--disable-background-timer-throttling')
		options.add_argument('--disable-backgrounding-occluded-windows')
		options.add_argument('--disable-renderer-backgrounding')
		options.add_argument('--disable-features=TranslateUI')
		options.add_argument('--disable-ipc-flooding-protection')
		options.add_argument('--memory-pressure-off')
		
		# Stealth options
		options.add_argument('--disable-blink-features=AutomationControlled')
		options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
		
		# Use headless mode in server environments (Docker, cloud platforms)
		# Set HEADLESS=false in .env to disable headless mode for local debugging
		if os.getenv('HEADLESS', 'true').lower() == 'true':
			options.add_argument('--headless')
			options.add_argument('--headless=new')  # Use new headless mode
			logger.info("Depop scraper running in headless mode (server environment)")
		else:
			logger.info("Depop scraper running in non-headless mode (local debugging)")
		
		options.add_experimental_option("excludeSwitches", ["enable-automation"])
		options.add_experimental_option('useAutomationExtension', False)
		try:
			# Try to use local chromedriver first, fall back to system PATH
			chromedriver_path = "./chromedriver"
			if not os.path.exists(chromedriver_path):
				# In Docker/cloud environments, chromedriver is in PATH
				chromedriver_path = "chromedriver"
			
			try:
				service = Service(chromedriver_path)
				self.driver = webdriver.Chrome(service=service, options=options)
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
									self.driver = webdriver.Chrome(service=service, options=options)
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
			self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
			self.driver.set_window_size(1440, 900)
			logger.info("Depop Chrome driver initialized successfully")
		except Exception as e:
			logger.error(f"Failed to initialize Depop Chrome driver: {e}")
			self.driver = None
	
	def search_listings(self, search_terms, max_pages=1, per_term_limit=40):
		if not self.driver:
			return []
		all_listings = []
		for i, term in enumerate(search_terms):
			try:
				logger.info(f"Searching Depop with Selenium for: {term}")
				found = self._search_term(term, max_pages=max_pages, limit=per_term_limit)
				all_listings.extend(found)
				
				# Restart driver every 8 searches to prevent session timeouts
				if (i + 1) % 8 == 0:
					logger.info("Restarting Depop driver to prevent session timeout")
					self.close()
					time.sleep(3)
					self.setup_driver()
					if self.driver is None:
						logger.error("Failed to restart Depop driver")
						break
				
				time.sleep(2)
			except Exception as e:
				logger.error(f"Depop search error for '{term}': {e}")
				# Try to restart driver on error
				try:
					self.close()
					time.sleep(2)
					self.setup_driver()
				except Exception as restart_error:
					logger.error(f"Failed to restart driver: {restart_error}")
		return all_listings
	
	def _search_term(self, term, max_pages=1, limit=40):
		results = []
		page = 1
		while page <= max_pages and len(results) < limit:
			try:
				search_url = f"{self.base_url}/search/?q={term.replace(' ', '+')}&sort=newest"
				logger.info(f"Navigating to: {search_url}")
				self.driver.get(search_url)
				
				# Wait for page to load
				time.sleep(5)
			except Exception as e:
				logger.warning(f"Session error for '{term}', attempting to reconnect: {e}")
				try:
					self.close()
					time.sleep(2)
					self.setup_driver()
					if self.driver is None:
						logger.error(f"Failed to reconnect for '{term}'")
						break
					search_url = f"{self.base_url}/search/?q={term.replace(' ', '+')}&sort=newest"
					logger.info(f"Reconnected, navigating to: {search_url}")
					self.driver.get(search_url)
					time.sleep(5)
				except Exception as reconnect_error:
					logger.error(f"Failed to reconnect for '{term}': {reconnect_error}")
					break
			
			try:
				# Get all product links
				items = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
				logger.info(f"Found {len(items)} Depop product links")
				
				seen_ids = set()
				for item in items[:limit]:
					try:
						href = item.get_attribute('href') or ''
						if not href or '/products/' not in href:
							continue
						
						# Extract product ID from URL
						m = re.search(r"/products/([\w-]+)", href)
						if not m:
							continue
						pid = m.group(1)
						if pid in seen_ids:
							continue
						seen_ids.add(pid)
						
						# Extract title from URL slug (this is the key insight!)
						clean_href = href.rstrip('/')
						slug = clean_href.split('/')[-1]
						title = slug.replace('-', ' ').title()
						
						# Get image - try to get higher resolution
						image_url = ''
						try:
							img_els = item.find_elements(By.CSS_SELECTOR, "img")
							for img in img_els:
								src = img.get_attribute('src') or img.get_attribute('data-src')
								if src and ('http' in src or src.startswith('//')):
									# Try to get higher resolution by modifying URL
									if 'depop.com' in src:
										# Replace small sizes with larger ones
										image_url = src.replace('/P2.jpg', '/P1.jpg')  # 640px instead of 150px
										image_url = image_url.replace('/P4.jpg', '/P1.jpg')  # 640px instead of 210px
										image_url = image_url.replace('/P5.jpg', '/P1.jpg')  # 640px instead of 320px
										image_url = image_url.replace('/P6.jpg', '/P1.jpg')  # 640px instead of 480px
									else:
										image_url = src
									break
						except Exception:
							pass
						
						# Filter items based on search term to ensure relevance
						t_lower = title.lower()
						if self._matches_search_term(t_lower, term):
							results.append({
								'listing_id': pid,
								'platform': 'Depop',
								'title': title,
								'price': 'Price not available',
								'url': href,
								'image_url': image_url,
								'search_term': term
							})
							
							if len(results) >= limit:
								break
							
					except Exception as e:
						logger.debug(f"Error processing Depop item: {e}")
						continue
			except Exception as e:
				logger.warning(f"Error processing Depop page for '{term}': {e}")
				# Try to continue with next page or break if it's a session issue
				if "invalid session id" in str(e).lower():
					logger.error(f"Session lost for '{term}', stopping search")
					break
			
			logger.info(f"Found {len(results)} Depop listings for '{term}'")
			page += 1
			
		return results
	
	def _extract_products_from_json(self, json_data, term):
		"""Extract product information from Depop's JSON data"""
		products = []
		
		try:
			# Navigate through the JSON structure to find products
			def find_products_recursive(obj, path=""):
				if isinstance(obj, dict):
					for key, value in obj.items():
						if key == 'products' and isinstance(value, list):
							for product in value:
								if isinstance(product, dict):
									title = product.get('title', '')
									slug = product.get('slug', '')
									product_id = product.get('id', '')
									
									# Use title or slug for filtering
									search_text = f"{title} {slug}".lower()
									if self._matches_search_term(search_text, term):
										# Get price
										price = 'Price not available'
										pricing = product.get('pricing', {})
										if pricing:
											final_price = pricing.get('final_price_key', 'original_price')
											price_data = pricing.get(final_price, {})
											if price_data:
												total_price = price_data.get('total_price', '')
												if total_price:
													price = f"${total_price}"
										
										# Get image
										image_url = ''
										preview = product.get('preview', {})
										if preview:
											image_url = preview.get('640', preview.get('480', preview.get('320', '')))
										
										products.append({
											'listing_id': str(product_id),
											'platform': 'Depop',
											'title': title or slug.replace('-', ' ').title(),
											'price': price,
											'url': f"https://www.depop.com/products/{slug}",
											'image_url': image_url,
											'search_term': term
										})
						else:
							find_products_recursive(value, f"{path}.{key}")
				elif isinstance(obj, list):
					for i, item in enumerate(obj):
						find_products_recursive(item, f"{path}[{i}]")
			
			find_products_recursive(json_data)
			
		except Exception as e:
			logger.debug(f"Error extracting products from JSON: {e}")
		
		return products
	
	def _matches_search_term(self, title, search_term):
		"""Check if the title matches the search term criteria"""
		title_lower = title.lower() if isinstance(title, str) else str(title).lower()
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
			# Check if it's a false positive
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
		important_words = [w for w in search_words if w not in ['vintage', '80s', '90s', 'the', 'a', 'an', 'and', 'or']]
		if len(important_words) >= 2:
			matches = sum(1 for word in important_words if word in title_lower)
			return matches >= 2
		
		# Fallback: require at least one key word
		return any(word in title_lower for word in important_words if len(word) > 3)
	
	def close(self):
		if self.driver:
			self.driver.quit()
			logger.info("Depop Chrome driver closed")
