# Quick Variable Setup Guide

## Railway CLI is Installed! ✅

Railway CLI is installed at `/Users/geno/.npm-global/bin/railway`

## Step-by-Step Setup

### 1. Reload Your Shell (to get Railway in PATH)

```bash
source ~/.zshrc
```

Or just open a new terminal window.

### 2. Login to Railway

```bash
railway login
```

This will open a browser window for authentication.

### 3. Link Your Project

```bash
cd /Users/geno/Desktop/clothesScraper/reverseweave-scrape
railway link
```

Select your Railway project when prompted.

### 4. Set Variables from .env File

Make sure your `.env` file has real values (not placeholders), then run:

```bash
./set_railway_vars.sh
```

Or set them manually:

```bash
railway variables set EMAIL_USER=your_email@gmail.com
railway variables set EMAIL_PASSWORD=your_app_password
railway variables set RECIPIENT_EMAIL=your_email@gmail.com
railway variables set SMTP_SERVER=smtp.gmail.com
railway variables set SMTP_PORT=587
railway variables set HEADLESS=true
```

### 5. Verify Variables Are Set

```bash
railway variables
```

You should see all 6 variables listed.

### 6. Check Railway Logs

Go to Railway dashboard → Your service → Logs

You should see "Email sent successfully" instead of "Email configuration missing".

## Troubleshooting

### "railway: command not found"

If you get this error, add to PATH:

```bash
export PATH="$PATH:$HOME/.npm-global/bin"
```

Or add this line to your `~/.zshrc`:
```bash
export PATH="$PATH:$HOME/.npm-global/bin"
```

Then reload:
```bash
source ~/.zshrc
```

### "Cannot login in non-interactive mode"

Run `railway login` manually in your terminal (not through a script).

### Variables Not Working

1. Check Railway logs for errors
2. Verify variables: `railway variables`
3. Make sure you're setting them on the service (not just project level)

## Quick Commands

```bash
# Login (first time)
railway login

# Link project (first time)
railway link

# Set all variables from .env
./set_railway_vars.sh

# View all variables
railway variables

# Set a single variable
railway variables set KEY=value
```

