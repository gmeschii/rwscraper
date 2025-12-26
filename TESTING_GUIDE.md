# Testing Guide - Before Cloud Deployment

This guide will help you test everything locally before deploying to the cloud.

## Step 1: Add Your Search Terms

Edit `main.py` and add your search terms to the `SEARCH_TERMS` list (around line 33):

```python
SEARCH_TERMS = [
    "navy champion reverse weave",
    "yale champion reverse weave", 
    # ... existing terms ...
    "army champion reverse weave",
    # Add your new terms here:
    "brown champion reverse weave",
    "gray champion reverse weave",
    # etc.
]
```

**Format**: Each term should be lowercase and include "champion reverse weave" or similar variations.

## Step 2: Verify Environment Setup

Make sure you have a `.env` file with your email settings:

```bash
# Check if .env exists
ls -la .env

# If not, create it from template
cp env_template.txt .env
nano .env  # or use your preferred editor
```

Required variables:
- `EMAIL_USER` - Your Gmail address
- `EMAIL_PASSWORD` - Gmail app password (NOT your regular password)
- `RECIPIENT_EMAIL` - Where to send notifications
- `SMTP_SERVER=smtp.gmail.com`
- `SMTP_PORT=587`

### Getting Gmail App Password:
1. Enable 2-factor authentication on Gmail
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Generate password for "Mail"
4. Use that password in `EMAIL_PASSWORD`

## Step 3: Test Locally

### Option A: Quick Test (Recommended)

Run the test script that does a single cycle:

```bash
# Make sure you're in the project directory
cd /path/to/reverseweave-scrape

# Activate virtual environment (if using one)
source venv/bin/activate  # or: python3 -m venv venv && source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the test
python3 test_local.py
```

This will:
- ✅ Test all search terms
- ✅ Check eBay and Depop
- ✅ Verify email sending (if new listings found)
- ✅ Show you what's happening (non-headless mode)
- ✅ Exit after one cycle (won't run forever)

### Option B: Full Test Run

Run the actual bot for a short time:

```bash
# Set HEADLESS=false to see the browser (optional)
export HEADLESS=false

# Run the bot (will run continuously)
python3 main.py

# Press Ctrl+C to stop after you see it working
```

## Step 4: Check Results

After testing, check:

1. **Logs**: `champion_monitor.log`
   ```bash
   tail -f champion_monitor.log
   ```

2. **Database**: `champion_listings.db` (should be created)
   ```bash
   ls -lh champion_listings.db
   ```

3. **Email**: Check your inbox for test notifications

## Step 5: Test Docker Build (Optional but Recommended)

Test that the Docker image builds correctly:

```bash
# Build the Docker image
docker build -t champion-monitor-test .

# If build succeeds, you're good to go!
# (You don't need to run it locally unless you want to)
```

## Common Issues & Solutions

### Issue: "ChromeDriver not found"
**Solution**: The code will auto-download it. If on Mac, you might need Chrome installed:
```bash
# Mac: Install Chrome via Homebrew or download from google.com/chrome
# Linux: Already handled in Dockerfile
```

### Issue: "Email not sending"
**Solution**: 
- Verify you're using an **app password**, not your regular Gmail password
- Check that 2FA is enabled
- Test SMTP connection:
  ```python
  python3 -c "import smtplib; s = smtplib.SMTP('smtp.gmail.com', 587); s.starttls(); print('SMTP OK')"
  ```

### Issue: "No listings found"
**Solution**: 
- This is normal if no new listings match your search terms
- Check logs to see if scraping is working
- Try a more common search term to verify scraping works

### Issue: "Selenium errors"
**Solution**:
- Make sure Chrome/Chromium is installed
- Try setting `HEADLESS=false` in `.env` to see what's happening
- Check that you have internet connection

## What to Look For

✅ **Success indicators:**
- Log shows "Starting monitoring cycle"
- Log shows "Checking eBay..." and "Checking Depop..."
- Log shows "Found X listings" (even if 0 is OK)
- No error messages
- Database file is created
- Email sent (if new listings found)

❌ **Failure indicators:**
- Import errors
- ChromeDriver errors
- SMTP/email errors
- Database errors

## Ready to Deploy?

Once your test passes:
1. ✅ Search terms added
2. ✅ Test run completed successfully
3. ✅ Email sending works
4. ✅ Docker build works (optional but recommended)

Then follow the **CLOUD_DEPLOYMENT.md** guide to deploy!

## Quick Test Checklist

- [ ] Added all desired search terms to `main.py`
- [ ] `.env` file configured with email settings
- [ ] Ran `python3 test_local.py` successfully
- [ ] Checked `champion_monitor.log` for errors
- [ ] Verified email sending (if listings found)
- [ ] Docker build works (optional)
- [ ] Ready to deploy! 🚀

