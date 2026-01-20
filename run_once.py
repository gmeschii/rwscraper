#!/usr/bin/env python3
"""
One-time execution script for GitHub Actions or cron jobs.
Runs a single monitoring cycle and exits.
"""
import sys
import traceback

try:
    from main import VintageClothingMonitorBot
except ImportError as e:
    print(f"ERROR: Failed to import main module: {e}")
    traceback.print_exc()
    sys.exit(2)
except Exception as e:
    print(f"ERROR: Unexpected error importing: {e}")
    traceback.print_exc()
    sys.exit(2)

if __name__ == "__main__":
    try:
        print("Initializing Vintage Clothing Monitor Bot...")
        bot = VintageClothingMonitorBot()
        print("Bot initialized successfully")
        
        # Check if database is empty (new deployment) and seed it
        if bot.is_database_empty():
            print("New deployment detected - seeding database with current listings...")
            try:
                bot.seed_database_with_current_listings()
                print("Database seeding completed")
            except Exception as e:
                print(f"WARNING: Error seeding database: {e}")
                traceback.print_exc()
                print("Continuing with normal monitoring - some duplicates may appear")
        
        # Run one monitoring cycle
        print("Starting monitoring cycle...")
        try:
            bot.run_monitoring_cycle()
            print("Monitoring cycle completed successfully")
            sys.exit(0)
        except Exception as e:
            print(f"ERROR: Error in monitoring cycle: {e}")
            traceback.print_exc()
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Fatal error: {e}")
        traceback.print_exc()
        sys.exit(2)

