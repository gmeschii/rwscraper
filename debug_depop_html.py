#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

def debug_depop_html():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service("./chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        search_url = "https://www.depop.com/search/?q=champion+reverse+weave&sort=newest"
        print(f"Navigating to: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        
        # Find product links
        items = driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
        print(f"Found {len(items)} product links")
        
        # Check first few items
        for i, item in enumerate(items[:3]):
            print(f"\n=== Item {i+1} ===")
            href = item.get_attribute('href')
            print(f"URL: {href}")
            
            # Try different ways to get title
            title_methods = [
                ("aria-label", item.get_attribute('aria-label')),
                ("text", item.text.strip()),
                ("title", item.get_attribute('title')),
            ]
            
            for method, value in title_methods:
                print(f"{method}: {value}")
            
            # Try to find child elements
            try:
                child_elements = item.find_elements(By.CSS_SELECTOR, "*")
                print(f"Child elements: {len(child_elements)}")
                for j, child in enumerate(child_elements[:5]):
                    print(f"  Child {j+1}: {child.tag_name} - {child.text.strip()[:50]}")
            except Exception as e:
                print(f"Error getting children: {e}")
            
            print("-" * 50)
        
        # Save page source for inspection
        with open('depop_debug.html', 'w') as f:
            f.write(driver.page_source)
        print("\nSaved page source to depop_debug.html")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_depop_html()

