#!/usr/bin/env python3
# Test script for Champion Reverse Weave Monitor Bot

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import requests
        import bs4
        import schedule
        import sqlite3
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from fake_useragent import UserAgent
        logger.info("✓ All required modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database creation and operations"""
    try:
        import sqlite3
        
        # Test database creation
        conn = sqlite3.connect('test_champion_listings.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id TEXT UNIQUE,
                platform TEXT,
                title TEXT,
                price TEXT,
                url TEXT,
                image_url TEXT,
                search_term TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test insert
        cursor.execute('''
            INSERT OR IGNORE INTO test_listings 
            (listing_id, platform, title, price, url, image_url, search_term)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('test123', 'Test', 'Test Listing', '$50', 'http://test.com', 'http://test.jpg', 'test search'))
        
        conn.commit()
        conn.close()
        
        # Clean up test database
        os.remove('test_champion_listings.db')
        
        logger.info("✓ Database operations working correctly")
        return True
    except Exception as e:
        logger.error(f"✗ Database error: {e}")
        return False

def test_email_config():
    """Test email configuration"""
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    if not email_user:
        logger.warning("⚠️  EMAIL_USER not set in .env file")
        return False
    if not email_password:
        logger.warning("⚠️  EMAIL_PASSWORD not set in .env file")
        return False
    if not recipient_email:
        logger.warning("⚠️  RECIPIENT_EMAIL not set in .env file")
        return False
    
    logger.info("✓ Email configuration found")
    return True

def test_scrapers():
    """Test scraper imports and basic functionality"""
    try:
        from ebay_scraper import EbayScraper
        from depop_scraper import DepopScraper
        
        # Test scraper initialization
        ebay_scraper = EbayScraper()
        depop_scraper = DepopScraper()
        
        logger.info("✓ Scrapers initialized successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Scraper error: {e}")
        return False

def main():
    print("🏆 Champion Reverse Weave Monitor Bot - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Database Operations", test_database),
        ("Email Configuration", test_email_config),
        ("Scraper Initialization", test_scrapers),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready to run.")
        print("\nNext steps:")
        print("1. Make sure your .env file is configured")
        print("2. Run: python3 main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("- Run: python3 setup.py")
        print("- Check .env file configuration")
        print("- Install missing dependencies")

if __name__ == "__main__":
    main()
