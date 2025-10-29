# Champion Reverse Weave Monitor Bot - Raspberry Pi Setup Guide

## Prerequisites

- Raspberry Pi (3B+ or newer recommended)
- MicroSD card (16GB+ recommended)
- Internet connection
- Tailscale account (optional but recommended)

## Step 1: Install Raspberry Pi OS

1. Download Raspberry Pi Imager from https://www.raspberrypi.org/downloads/
2. Flash Raspberry Pi OS Lite (64-bit) to your microSD card
3. Enable SSH and set up WiFi during imaging process
4. Boot your Raspberry Pi

## Step 2: Initial Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y
```

## Step 3: Install Tailscale (Recommended)

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale
sudo tailscale up

# Follow the authentication link to connect your device
```

## Step 4: Clone and Setup the Bot

```bash
# Clone the repository (or copy files)
git clone <your-repo-url> champion-monitor
cd champion-monitor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Run setup script
python3 setup.py
```

## Step 5: Configure Email Settings

```bash
# Edit the .env file
nano .env
```

Fill in your email configuration:
```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Gmail Setup:
1. Enable 2-factor authentication on your Gmail account
2. Generate an app password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in EMAIL_PASSWORD

## Step 6: Test the Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Test run (will run once and exit)
python3 main.py
```

## Step 7: Set Up as a Service (Auto-start)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/champion-monitor.service
```

Add the following content:
```ini
[Unit]
Description=Champion Reverse Weave Monitor Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/champion-monitor
Environment=PATH=/home/pi/champion-monitor/venv/bin
ExecStart=/home/pi/champion-monitor/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable champion-monitor.service

# Start the service
sudo systemctl start champion-monitor.service

# Check status
sudo systemctl status champion-monitor.service
```

## Step 8: Monitor Logs

```bash
# View logs
tail -f champion_monitor.log

# Or view service logs
sudo journalctl -u champion-monitor.service -f
```

## Step 9: Optional - Set Up Cron Backup

Create a backup script:
```bash
nano backup.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp champion_listings.db "backups/champion_listings_$DATE.db"
# Keep only last 7 days of backups
find backups/ -name "champion_listings_*.db" -mtime +7 -delete
```

Make executable and add to cron:
```bash
chmod +x backup.sh
crontab -e
```

Add:
```
0 2 * * * /home/pi/champion-monitor/backup.sh
```

## Troubleshooting

### Service won't start:
```bash
# Check service status
sudo systemctl status champion-monitor.service

# Check logs
sudo journalctl -u champion-monitor.service --no-pager
```

### Email not working:
- Verify EMAIL_PASSWORD is an app password, not your regular password
- Check SMTP settings for your email provider
- Test with a simple Python script first

### Bot not finding listings:
- Check internet connection
- Verify search terms in main.py
- Check logs for scraping errors

### Memory issues:
- Monitor memory usage: `free -h`
- Consider reducing MAX_PAGES in .env
- Add swap if needed: `sudo dphys-swapfile swapoff && sudo dphys-swapfile swapon`

## Remote Access via Tailscale

Once Tailscale is set up:
1. Access your Pi from any device: `ssh pi@<tailscale-ip>`
2. View logs remotely: `tail -f champion_monitor.log`
3. Manage the service: `sudo systemctl restart champion-monitor.service`

## Maintenance

### Update the bot:
```bash
cd champion-monitor
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart champion-monitor.service
```

### Clean up old logs:
```bash
# Keep only last 30 days of logs
find . -name "*.log" -mtime +30 -delete
```

## Security Notes

- Change default Pi password
- Use SSH keys instead of password authentication
- Keep system updated
- Consider using a firewall
- Monitor for unusual activity

## Performance Tips

- Use a fast microSD card (Class 10 or better)
- Ensure stable internet connection
- Monitor CPU and memory usage
- Consider running during off-peak hours if bandwidth is limited
