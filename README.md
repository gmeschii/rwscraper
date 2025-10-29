# Champion Reverse Weave Monitor Bot

A Python bot that monitors eBay and Depop for new Champion reverse weave listings and sends email notifications. Perfect for running on a Raspberry Pi with Tailscale for remote access.

## Features

- 🔍 Monitors 16+ specific Champion reverse weave search terms
- 📧 Sends hourly email notifications with HTML formatting
- 🖼️ Includes listing images for easy visual identification
- 🚫 Prevents duplicate notifications using SQLite database
- 🕐 Runs continuously with hourly checks
- 🍓 Optimized for Raspberry Pi deployment
- 🔒 Secure email configuration with app passwords

## Search Terms Monitored

- Navy Champion Reverse Weave
- Yale Champion Reverse Weave
- Stanford Champion Reverse Weave
- Princeton Champion Reverse Weave
- Penn Champion Reverse Weave
- Columbia Champion Reverse Weave
- Harvard Champion Reverse Weave
- Dartmouth Champion Reverse Weave
- Cornell Champion Reverse Weave
- Cal Champion Reverse Weave
- Berkeley Champion Reverse Weave
- Vintage Champion Reverse Weave
- Black Champion Reverse Weave
- 80s Champion Reverse Weave
- 90s Champion Reverse Weave
- Army Champion Reverse Weave

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <your-repo-url> champion-monitor
   cd champion-monitor
   python3 setup.py
   ```

2. **Configure email:**
   ```bash
   cp env_template.txt .env
   nano .env
   ```
   
   Fill in your email settings (see Gmail setup below).

3. **Run the bot:**
   ```bash
   python3 main.py
   ```

## Gmail Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an app password:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in `EMAIL_PASSWORD`

## Raspberry Pi Deployment

See [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md) for detailed instructions on:
- Setting up Raspberry Pi OS
- Installing Tailscale for remote access
- Running as a systemd service
- Monitoring and maintenance

## Configuration

Edit `.env` file to customize:

```env
# Email Configuration
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=your_email@gmail.com

# SMTP Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Optional: Custom search terms
CUSTOM_SEARCH_TERMS=navy champion reverse weave,yale champion reverse weave

# Optional: Monitoring frequency (minutes)
MONITORING_FREQUENCY=60

# Optional: Scraping limits
MAX_PAGES_EBAY=3
MAX_PAGES_DEPOP=2
```

## File Structure

```
champion-monitor/
├── main.py                 # Main bot application
├── ebay_scraper.py         # eBay scraping logic
├── depop_scraper.py        # Depop scraping logic
├── requirements.txt        # Python dependencies
├── setup.py               # Setup script
├── env_template.txt       # Environment template
├── RASPBERRY_PI_SETUP.md  # Pi setup instructions
├── champion_listings.db   # SQLite database (created automatically)
└── champion_monitor.log   # Log file (created automatically)
```

## How It Works

1. **Scraping**: Bot searches eBay and Depop using web scraping and APIs
2. **Filtering**: Only Champion reverse weave items are included
3. **Deduplication**: SQLite database tracks seen listings to prevent duplicates
4. **Email**: HTML emails sent hourly with new listings and images
5. **Scheduling**: Runs continuously with hourly checks

## Troubleshooting

### Email Issues
- Verify app password (not regular password)
- Check SMTP settings for your provider
- Test with simple Python script first

### No Listings Found
- Check internet connection
- Verify search terms
- Check logs for scraping errors
- Sites may have changed their structure

### Service Issues (Raspberry Pi)
```bash
# Check service status
sudo systemctl status champion-monitor.service

# View logs
sudo journalctl -u champion-monitor.service -f

# Restart service
sudo systemctl restart champion-monitor.service
```

## Legal and Ethical Considerations

- **Respectful Scraping**: Bot includes delays between requests
- **Rate Limiting**: Configurable limits on pages scraped
- **Terms of Service**: Ensure compliance with eBay and Depop ToS
- **Personal Use**: Designed for personal monitoring only

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for personal use only. Please respect the terms of service of the platforms being monitored.
