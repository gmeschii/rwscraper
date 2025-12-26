# Railway Deployment - Step-by-Step Guide

## Complete Step-by-Step Instructions

Follow these steps in order to deploy your bot to Railway.

---

## Prerequisites Checklist

Before starting, make sure you have:
- [ ] Code ready and tested locally
- [ ] GitHub account
- [ ] Gmail account (for email notifications)
- [ ] Gmail app password ready (see Step 2 below)

---

## Step 1: Prepare Your Code for GitHub

### 1.1 Check if you have a Git repository

```bash
# In your project directory
cd /Users/geno/Desktop/clothesScraper/reverseweave-scrape
git status
```

**If you see "not a git repository":**
```bash
# Initialize git
git init
git add .
git commit -m "Initial commit - Ready for Railway deployment"
```

**If you already have git:**
```bash
# Make sure everything is committed
git add .
git commit -m "Ready for Railway deployment"
```

### 1.2 Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click the **"+"** icon in top right → **"New repository"**
3. Fill in:
   - **Repository name**: `reverseweave-scrape` (or your choice)
   - **Description**: "Vintage clothing monitor bot"
   - **Visibility**: Private (recommended) or Public
   - **DO NOT** check "Initialize with README" (you already have files)
4. Click **"Create repository"**

### 1.3 Push Code to GitHub

GitHub will show you commands. Use these (replace `YOUR_USERNAME` with your GitHub username):

```bash
# If you just initialized git (Step 1.1)
git remote add origin https://github.com/YOUR_USERNAME/reverseweave-scrape.git
git branch -M main
git push -u origin main

# If you already had git set up
git remote add origin https://github.com/YOUR_USERNAME/reverseweave-scrape.git
git push -u origin main
```

**Enter your GitHub username/password when prompted**

✅ **Step 1 Complete**: Your code is now on GitHub!

---

## Step 2: Get Gmail App Password

**Important**: You need a Gmail App Password (NOT your regular password)

### 2.1 Enable 2-Factor Authentication

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **"Security"** in left sidebar
3. Under "How you sign in to Google", click **"2-Step Verification"**
4. Follow prompts to enable 2FA (if not already enabled)

### 2.2 Generate App Password

1. Still in Security settings, scroll to **"2-Step Verification"**
2. Click **"App passwords"** (at the bottom)
3. You may need to sign in again
4. Select **"Mail"** from dropdown
5. Select **"Other (Custom name)"** → Enter "Railway Bot"
6. Click **"Generate"**
7. **Copy the 16-character password** (you'll need this in Step 4)

**Example**: `abcd efgh ijkl mnop`

✅ **Step 2 Complete**: You have your Gmail app password!

---

## Step 3: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"** or **"Login"**
3. Click **"Login with GitHub"**
4. Authorize Railway to access your GitHub account
5. You'll be taken to Railway dashboard

✅ **Step 3 Complete**: Railway account created!

---

## Step 4: Deploy from GitHub

### 4.1 Create New Project

1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. You'll see a list of your GitHub repositories
4. Find and click on **"reverseweave-scrape"** (or whatever you named it)

### 4.2 Railway Auto-Detection

Railway will automatically:
- Detect your Dockerfile
- Start building your project
- Show build progress

**Wait for build to complete** (takes 2-5 minutes)

You'll see logs like:
```
Building Docker image...
Installing dependencies...
Setting up Chrome...
```

✅ **Step 4 Complete**: Railway is building your project!

---

## Step 5: Configure Environment Variables

**Critical**: This step is required for the bot to work!

### 5.1 Open Variables Tab

1. In Railway dashboard, click on your service (should be named "reverseweave-scrape")
2. Click on the **"Variables"** tab
3. Click **"New Variable"** for each variable below

### 5.2 Add Required Variables

Add these **6 variables** one by one:

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `EMAIL_USER` | `your_email@gmail.com` | Your Gmail address |
| `EMAIL_PASSWORD` | `your_app_password` | The 16-char password from Step 2 |
| `RECIPIENT_EMAIL` | `your_email@gmail.com` | Where to send notifications |
| `SMTP_SERVER` | `smtp.gmail.com` | Gmail SMTP server |
| `SMTP_PORT` | `587` | Gmail SMTP port |
| `HEADLESS` | `true` | Required for Railway |

**How to add each:**
1. Click **"New Variable"**
2. Enter variable name (e.g., `EMAIL_USER`)
3. Enter value (e.g., `your_email@gmail.com`)
4. Click **"Add"**
5. Repeat for all 6 variables

### 5.3 Verify Variables

After adding all 6, you should see:
```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
HEADLESS=true
```

✅ **Step 5 Complete**: Environment variables configured!

---

## Step 6: Verify Deployment

### 6.1 Check Service Status

1. Go to Railway dashboard
2. Click on your service
3. Check **"Deployments"** tab
4. Status should be **"Active"** (green)

### 6.2 Check Logs

1. Click on **"Logs"** tab
2. You should see logs like:
   ```
   Database initialized successfully
   Starting monitoring cycle
   Checking eBay...
   Checking Depop...
   ```

**Good signs:**
- ✅ "Starting monitoring cycle"
- ✅ "Checking eBay..."
- ✅ "Checking Depop..."
- ✅ No ERROR messages

**Warning signs:**
- ❌ "Driver not initialized"
- ❌ "Email configuration missing"
- ❌ Service status "Restarting"

### 6.3 First Monitoring Cycle

- The bot runs every hour
- First cycle starts immediately after deployment
- Check logs after 5-10 minutes to see if it's working

✅ **Step 6 Complete**: Deployment verified!

---

## Step 7: Test Email Notifications

### 7.1 Wait for First Cycle

- Bot runs every hour
- First cycle happens within first hour
- If new listings are found, you'll get an email

### 7.2 Check Your Email

- Check the inbox for `RECIPIENT_EMAIL`
- Look for subject: "New Vintage Clothing Listings"
- If you get an email, it's working! 🎉

**Note**: If no listings found, that's normal - it means no new matching items were posted.

---

## Troubleshooting

### Issue: Build Failed

**Check:**
- Railway logs for error messages
- Make sure Dockerfile is in root directory
- Verify all files are pushed to GitHub

**Fix:**
- Check logs for specific error
- Fix locally, commit, push
- Railway will rebuild automatically

### Issue: Service Keeps Restarting

**Check:**
- Railway logs for error messages
- Verify all environment variables are set
- Check for import errors

**Fix:**
- Most common: Missing environment variable
- Add missing variable in Railway dashboard
- Service will restart automatically

### Issue: No Emails Received

**Check:**
- Railway logs for "Email configuration missing"
- Verify `EMAIL_PASSWORD` is app password (not regular password)
- Check spam folder

**Fix:**
- Verify all email variables are set correctly
- Make sure you're using Gmail app password
- Check Railway logs for email errors

### Issue: "Driver not initialized"

**Check:**
- Railway logs for ChromeDriver errors
- This is rare on Railway (Linux environment)

**Fix:**
- Usually resolves on next deployment
- Code has fallback to ChromeDriverManager

---

## Updating Your Bot

**Super easy!** Just push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update: description of changes"
git push
```

Railway automatically:
- Detects the push
- Rebuilds Docker image
- Redeploys service
- Takes 2-5 minutes

---

## Monitoring Your Bot

### Railway Dashboard

- **Logs Tab**: Real-time logs (like `champion_monitor.log`)
- **Metrics Tab**: CPU, Memory usage
- **Deployments Tab**: History of all deployments
- **Variables Tab**: Environment variables

### What to Monitor

**Daily (first week):**
- Check logs for errors
- Verify service is "Active"
- Check for email notifications

**Weekly (after first week):**
- Quick check that it's still running
- Review any error patterns

---

## Cost

- **Free tier**: $5 credit/month
- **After credit**: ~$5-7/month (depending on usage)
- **Your bot**: Low resource usage, should stay in free tier or low cost

---

## Quick Reference

### Required Environment Variables
```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
HEADLESS=true
```

### Update Process
```bash
git add .
git commit -m "Update: description"
git push
# Railway auto-deploys in 2-5 minutes
```

### Check Logs
- Railway Dashboard → Your Service → Logs Tab

---

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] Project deployed from GitHub
- [ ] All 6 environment variables set
- [ ] Service status is "Active"
- [ ] Logs show "Starting monitoring cycle"
- [ ] No error messages in logs
- [ ] Bot is running! 🎉

---

## Need Help?

1. **Check Railway logs** - Most errors are visible there
2. **See QUICK_FIXES.md** - Common issues and solutions
3. **Check ERROR_PREVENTION.md** - Error prevention guide

---

## You're Done! 🚀

Your bot is now running 24/7 on Railway! It will:
- Check eBay and Depop every hour
- Find new listings matching your search terms
- Send you email notifications
- Run automatically without any maintenance

Enjoy your automated vintage clothing monitor! 🎉

