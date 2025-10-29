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

logger = logging.getLogger(__name__)

class DepopSeleniumScraper:
	def __init__(self):
		self.base_url = "https://www.depop.com"
		self.driver = None
		self.setup_driver()
	
	def setup_driver(self):
		options = Options()
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		options.add_argument('--disable-blink-features=AutomationControlled')
		options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
		# options.add_argument('--headless')  # toggle if desired
		options.add_experimental_option("excludeSwitches", ["enable-automation"])
		options.add_experimental_option('useAutomationExtension', False)
		try:
			service = Service("./chromedriver")
			self.driver = webdriver.Chrome(service=service, options=options)
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
						
						# Filter for Champion reverse weave - be more lenient
						t_lower = title.lower()
						if 'champion' in t_lower and ('reverse' in t_lower or 'weave' in t_lower):
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
									if 'champion' in search_text and any(k in search_text for k in ['reverse weave','reverse-weave','reverseweave']):
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
	
	def close(self):
		if self.driver:
			self.driver.quit()
			logger.info("Depop Chrome driver closed")
