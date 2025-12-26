# Railway Quick Start - TL;DR

## The 7 Steps (5-10 minutes total)

### 1. Push to GitHub (2 min)
```bash
cd /Users/geno/Desktop/clothesScraper/reverseweave-scrape
git init  # if needed
git add .
git commit -m "Ready for Railway"
# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/reverseweave-scrape.git
git push -u origin main
```

### 2. Get Gmail App Password (2 min)
- Go to [myaccount.google.com](https://myaccount.google.com) → Security
- Enable 2FA (if not already)
- Go to "App passwords" → Generate for "Mail"
- Copy the 16-character password

### 3. Create Railway Account (1 min)
- Go to [railway.app](https://railway.app)
- Click "Login with GitHub"
- Authorize Railway

### 4. Deploy from GitHub (1 min)
- Railway dashboard → "New Project"
- "Deploy from GitHub repo"
- Select your repository
- Wait for build (2-5 minutes)

### 5. Set Environment Variables (2 min)
In Railway → Your Service → Variables tab, add:

```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
HEADLESS=true
```

### 6. Verify (1 min)
- Check service status: Should be "Active"
- Check logs: Should see "Starting monitoring cycle"
- No errors = Success! ✅

### 7. Wait for First Email
- Bot runs every hour
- First cycle happens within first hour
- Check your email for notifications!

---

## That's It! 🎉

Your bot is now running 24/7 on Railway.

**For detailed instructions, see `RAILWAY_DEPLOYMENT_STEPS.md`**

