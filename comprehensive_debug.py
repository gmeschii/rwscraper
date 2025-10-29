#!/usr/bin/env python3
# Comprehensive debug of Selenium scraper

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def comprehensive_debug():
    print("🔍 Comprehensive Selenium Debug...")
    
    # Setup driver
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to eBay
        search_url = "https://www.ebay.com/sch/i.html?_nkw=champion+reverse+weave&_sop=10"
        print(f"Navigating to: {search_url}")
        
        driver.get(search_url)
        time.sleep(5)
        
        # Find items
        items = driver.find_elements(By.CSS_SELECTOR, "div[class*='s-item']")
        print(f"Found {len(items)} items")
        
        # Analyze first few items in detail
        for i, item in enumerate(items[:3]):
            print(f"\n--- Item {i+1} Analysis ---")
            
            # Get all text content
            try:
                all_text = item.text
                print(f"All text: {all_text[:200]}...")
            except:
                print("Could not get text content")
            
            # Get HTML content
            try:
                html = item.get_attribute('outerHTML')
                print(f"HTML: {html[:300]}...")
            except:
                print("Could not get HTML content")
            
            # Try to find any links
            try:
                links = item.find_elements(By.TAG_NAME, "a")
                print(f"Found {len(links)} links")
                for j, link in enumerate(links[:2]):
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    print(f"  Link {j+1}: {href[:50]}... - '{text[:30]}...'")
            except:
                print("Could not find links")
            
            # Try to find any images
            try:
                images = item.find_elements(By.TAG_NAME, "img")
                print(f"Found {len(images)} images")
                for j, img in enumerate(images[:2]):
                    src = img.get_attribute('src')
                    alt = img.get_attribute('alt')
                    print(f"  Image {j+1}: {src[:50]}... - '{alt[:30]}...'")
            except:
                print("Could not find images")
            
            # Check for Champion mentions
            if 'champion' in all_text.lower():
                print("✅ Contains 'champion'")
            else:
                print("❌ Does not contain 'champion'")
            
            # Check for reverse weave mentions
            if any(kw in all_text.lower() for kw in ['reverse weave', 'reverse-weave', 'reverseweave']):
                print("✅ Contains 'reverse weave'")
            else:
                print("❌ Does not contain 'reverse weave'")
        
        # Check page source for any Champion mentions
        page_source = driver.page_source.lower()
        champion_count = page_source.count('champion')
        print(f"\nTotal 'champion' mentions in page: {champion_count}")
        
        # Save page source for inspection
        with open('selenium_debug.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Saved page source to selenium_debug.html")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
    
    finally:
        driver.quit()
        print("🔒 Chrome driver closed")

if __name__ == "__main__":
    comprehensive_debug()
