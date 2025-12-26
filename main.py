# Vintage Clothing Monitor Bot
# Monitors eBay and Depop for new vintage clothing listings
# Sends hourly email notifications with no duplicates

import os
import sqlite3
import smtplib
import schedule
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('champion_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Search terms to monitor
SEARCH_TERMS = [
    # Champion Reverse Weave
    "navy champion reverse weave",
    "yale champion reverse weave", 
    "stanford champion reverse weave",
    "princeton champion reverse weave",
    "penn champion reverse weave",
    "columbia champion reverse weave",
    "harvard champion reverse weave",
    "dartmouth champion reverse weave",
    "cornell champion reverse weave",
    "cal champion reverse weave",
    "berkeley champion reverse weave",
    "vintage champion reverse weave",
    "black champion reverse weave",
    "80s champion reverse weave",
    "90s champion reverse weave",
    "army champion reverse weave",
    # North Face - Vintage 80s Puffer/Down Jackets
    "vintage 80s north face puffer",
    "vintage 80s north face down jacket",
    "80s north face puffer jacket",
    "vintage north face puffer",
    "vintage north face down jacket",
    "80s north face jacket",
    "vintage north face nuptse",
    "vintage north face mountain jacket",
    # Levi's - Vintage Black Made in USA
    "vintage black made in usa levi",
    "vintage black levi made in usa",
    "black levi made in usa",
    "vintage black levi jacket",
    "vintage black levi denim jacket",
    "vintage black levi trucker",
    "vintage black levi type 3",
    "vintage black levi sherpa",
    "vintage black levi corduroy",
    # Pendleton - Board Shirts and Loop Collars
    "vintage pendleton board shirt",
    "vintage pendleton loop collar",
    "pendleton board shirt",
    "pendleton loop collar",
    "vintage pendleton wool shirt",
    "vintage pendleton flannel",
    "pendleton made in usa shirt"
]

class VintageClothingMonitorBot:
    def __init__(self):
        self.db_path = 'champion_listings.db'
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database to track seen listings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seen_listings (
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
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def is_listing_seen(self, listing_id):
        """Check if a listing has already been seen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM seen_listings WHERE listing_id = ?', (listing_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def mark_listing_seen(self, listing_data):
        """Mark a listing as seen in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO seen_listings 
                (listing_id, platform, title, price, url, image_url, search_term)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                listing_data['listing_id'],
                listing_data['platform'],
                listing_data['title'],
                listing_data['price'],
                listing_data['url'],
                listing_data['image_url'],
                listing_data['search_term']
            ))
            conn.commit()
            logger.info(f"Marked listing {listing_data['listing_id']} as seen")
        except sqlite3.IntegrityError:
            logger.debug(f"Listing {listing_data['listing_id']} already exists in database")
        finally:
            conn.close()
    
    def send_email_notification(self, new_listings):
        """Send email notification with new listings"""
        if not new_listings:
            logger.info("No new listings to send")
            return
        
        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        email_user = os.getenv('EMAIL_USER')
        email_password = os.getenv('EMAIL_PASSWORD')
        recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        if not all([email_user, email_password, recipient_email]):
            logger.error("Email configuration missing. Please set EMAIL_USER, EMAIL_PASSWORD, and RECIPIENT_EMAIL")
            return
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New Vintage Clothing Listings - {len(new_listings)} items"
        msg['From'] = email_user
        msg['To'] = recipient_email
        
        # Create HTML content
        html_content = self.create_html_email(new_listings)
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent successfully with {len(new_listings)} listings")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    def create_html_email(self, listings):
        """Create HTML email content with listings grouped by search term - Gmail optimized"""
        # Group listings by search term
        grouped_listings = {}
        for listing in listings:
            search_term = listing['search_term']
            if search_term not in grouped_listings:
                grouped_listings[search_term] = []
            grouped_listings[search_term].append(listing)
        
        # Limit total listings to prevent Gmail truncation (max 50 listings)
        total_shown = 0
        max_listings = 50
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 15px; line-height: 1.4; }}
                .header {{ background: #3498db; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
                .search-group {{ margin: 15px 0; border: 1px solid #ddd; border-radius: 6px; overflow: hidden; }}
                .search-header {{ background: #f8f9fa; padding: 8px 12px; font-weight: bold; border-bottom: 1px solid #ddd; }}
                .listing {{ padding: 10px; border-bottom: 1px solid #eee; display: flex; align-items: center; }}
                .listing:last-child {{ border-bottom: none; }}
                .listing img {{ width: 80px; height: 80px; object-fit: cover; margin-right: 12px; border-radius: 4px; }}
                .listing-info {{ flex: 1; }}
                .price {{ font-size: 16px; font-weight: bold; color: #e74c3c; margin: 2px 0; }}
                .platform {{ background: #2ecc71; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-right: 8px; }}
                .title {{ font-size: 14px; margin: 2px 0; font-weight: bold; line-height: 1.3; }}
                .url {{ margin-top: 4px; }}
                .url a {{ color: #3498db; text-decoration: none; font-size: 12px; }}
                .no-image {{ width: 80px; height: 80px; background: #ecf0f1; border: 1px solid #bdc3c7; margin-right: 12px; display: flex; align-items: center; justify-content: center; color: #7f8c8d; font-size: 10px; border-radius: 4px; }}
                .summary {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2 style="margin: 0;">🏆 New Vintage Clothing Listings</h2>
                <p style="margin: 5px 0 0 0;">Found <strong>{len(listings)}</strong> new listings across <strong>{len(grouped_listings)}</strong> search terms</p>
            </div>
        """
        
        for search_term, term_listings in grouped_listings.items():
            if total_shown >= max_listings:
                html += f"""
                <div class="summary">
                    <strong>Note:</strong> Showing first {max_listings} listings to prevent email truncation. 
                    Total found: {len(listings)} listings.
                </div>
                """
                break
                
            html += f"""
            <div class="search-group">
                <div class="search-header">🔍 {search_term.title()} ({len(term_listings)} listings)</div>
            """
            
            for listing in term_listings[:10]:  # Limit to 10 per search term
                if total_shown >= max_listings:
                    break
                    
                # Handle missing images
                img_html = f'<img src="{listing["image_url"]}" alt="Listing Image" onerror="this.parentNode.innerHTML=\'<div class=\\"no-image\\">No Image</div>\'">' if listing['image_url'] else '<div class="no-image">No Image</div>'
                
                html += f"""
                <div class="listing">
                    {img_html}
                    <div class="listing-info">
                        <span class="platform">{listing['platform'].upper()}</span>
                        <div class="title">{listing['title']}</div>
                        <div class="price">{listing['price']}</div>
                        <div class="url">
                            <a href="{listing['url']}" target="_blank">View Listing →</a>
                        </div>
                    </div>
                </div>
                """
                total_shown += 1
            
            html += "</div>"
        
        html += """
            <div style="margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 4px; text-align: center;">
                <small>This email was sent by your Vintage Clothing Monitor Bot</small>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        logger.info("Starting monitoring cycle")
        
        new_listings = []
        
        # Import scrapers here to avoid circular imports
        try:
            from ebay_selenium_scraper import EbaySeleniumScraper
            from depop_selenium_scraper import DepopSeleniumScraper
        except ImportError as e:
            logger.error(f"Failed to import scrapers: {e}")
            return
        
        # Initialize scrapers
        ebay_scraper = EbaySeleniumScraper()
        depop_scraper = DepopSeleniumScraper()
        
        try:
            # Check eBay
            logger.info("Checking eBay...")
            # Limit per term to reduce noise but still get newest first
            ebay_listings = ebay_scraper.search_listings(SEARCH_TERMS)
            for listing in ebay_listings:
                if not self.is_listing_seen(listing['listing_id']):
                    new_listings.append(listing)
                    self.mark_listing_seen(listing)
            
            # Check Depop
            logger.info("Checking Depop...")
            depop_listings = depop_scraper.search_listings(SEARCH_TERMS, max_pages=1, per_term_limit=30)
            for listing in depop_listings:
                if not self.is_listing_seen(listing['listing_id']):
                    new_listings.append(listing)
                    self.mark_listing_seen(listing)
        
        finally:
            # Clean up Selenium driver
            if hasattr(ebay_scraper, 'close'):
                ebay_scraper.close()
        
        # Send email if there are new listings
        if new_listings:
            logger.info(f"Found {len(new_listings)} new listings")
            self.send_email_notification(new_listings)
        else:
            logger.info("No new listings found")
        
        logger.info("Monitoring cycle completed")
    
    def start_monitoring(self):
        """Start the monitoring bot"""
        logger.info("Starting Vintage Clothing Monitor Bot")
        
        # Schedule to run every hour
        schedule.every().hour.do(self.run_monitoring_cycle)
        
        # Run immediately on startup
        self.run_monitoring_cycle()
        
        # Keep the bot running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    bot = VintageClothingMonitorBot()
    bot.start_monitoring()
