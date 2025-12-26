# Railway Deployment Checklist ✅

## Pre-Deployment Validation Results

**Status: ✅ ALL CHECKS PASSED**

### Verified Components

- ✅ **Python Syntax** - All files have valid syntax
- ✅ **Python Imports** - All required modules are available
- ✅ **Search Terms** - 40 search terms configured including:
  - ✅ North Face Puffer (8 search terms)
  - ✅ Pendleton (7 search terms)
  - ✅ Black Levis (9 search terms)
  - ✅ Champion Reverse Weave (16 search terms)
- ✅ **Required Files** - All necessary files present
- ✅ **Dockerfile** - Properly configured for Railway
- ✅ **Railway Config** - railway.json is valid
- ✅ **Environment Template** - All variables documented
- ✅ **Requirements** - All dependencies listed
- ✅ **Code Imports** - All modules import successfully
- ✅ **Bot Initialization** - Bot can be instantiated

## Before Deploying to Railway

### 1. Environment Variables Setup

You'll need to set these in Railway dashboard (Variables tab):

```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
HEADLESS=true
```

**Important**: Use a Gmail App Password, not your regular password!
- Enable 2FA on Gmail
- Go to Google Account → Security → 2-Step Verification → App passwords
- Generate password for "Mail"

### 2. Git Repository

Make sure your code is pushed to GitHub:

```bash
# If not already done:
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### 3. Railway Deployment Steps

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables**
   - Go to your service → Variables tab
   - Add all environment variables listed above

4. **Deploy**
   - Railway will auto-detect Dockerfile
   - It will build and deploy automatically
   - Monitor logs in Railway dashboard

### 4. Post-Deployment Verification

After deployment, check:

- ✅ Service is running (green status in Railway)
- ✅ Logs show "Starting monitoring cycle"
- ✅ No error messages in logs
- ✅ Database is being created (champion_listings.db)
- ✅ Test email received (if new listings found)

## Quick Test Commands

### Local Testing (Optional)
```bash
# Run validation check
python3 pre_deployment_check.py

# Run test cycle (won't run forever)
python3 test_local.py
```

### Check Logs in Railway
- Go to Railway dashboard → Your service → Logs
- Look for "Starting monitoring cycle"
- Check for any error messages

## Troubleshooting

### If deployment fails:
1. Check Railway logs for errors
2. Verify all environment variables are set
3. Check Dockerfile builds correctly locally:
   ```bash
   docker build -t test-build .
   ```

### If bot doesn't run:
1. Check Railway logs
2. Verify Gmail app password is correct
3. Check that HEADLESS=true is set
4. Ensure service has enough resources (512MB+ RAM)

### If no emails sent:
1. Verify Gmail app password (not regular password)
2. Check SMTP settings
3. Check Railway logs for email errors
4. Verify RECIPIENT_EMAIL is correct

## Current Configuration

- **Search Terms**: 40 total
- **Platforms**: eBay + Depop
- **Monitoring Frequency**: Every hour
- **Database**: SQLite (champion_listings.db)
- **Email**: HTML formatted with images

## Ready to Deploy! 🚀

Everything has been validated and is ready for Railway deployment.

