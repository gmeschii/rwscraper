#!/usr/bin/env python3
"""
Test script to verify the bot works locally before deploying
This runs a single monitoring cycle and exits (doesn't run continuously)
"""

import os
import sys
from main import VintageClothingMonitorBot, SEARCH_TERMS

# Set headless to false for local testing so you can see what's happening
# (optional - you can set HEADLESS=true in .env if you prefer)
os.environ.setdefault('HEADLESS', 'false')

def test_bot():
    """Run a single test cycle"""
    print("=" * 60)
    print("🧪 Testing Vintage Clothing Monitor Bot")
    print("=" * 60)
    print(f"\n📋 Testing with {len(SEARCH_TERMS)} search terms:")
    for i, term in enumerate(SEARCH_TERMS, 1):
        print(f"   {i}. {term}")
    
    print("\n" + "=" * 60)
    print("Starting test run...")
    print("=" * 60 + "\n")
    
    try:
        bot = VintageClothingMonitorBot()
        
        # Run a single monitoring cycle
        print("Running monitoring cycle...")
        bot.run_monitoring_cycle()
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        print("\nCheck the following:")
        print("  - champion_monitor.log for detailed logs")
        print("  - champion_listings.db for stored listings")
        print("  - Email inbox (if new listings were found)")
        print("\nIf everything looks good, you're ready to deploy! 🚀")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ Test failed with error:")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease check:")
        print("  - .env file is configured correctly")
        print("  - Chrome/Chromium is installed (for local testing)")
        print("  - Internet connection is working")
        print("  - champion_monitor.log for more details")
        return False

if __name__ == "__main__":
    success = test_bot()
    sys.exit(0 if success else 1)

