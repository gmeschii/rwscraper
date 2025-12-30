# Setting Railway Variables from Local File

## Important Security Note

**NEVER commit your `.env` file to git!** It contains sensitive passwords.

The `.env` file should be in `.gitignore` (which it already is).

## Method 1: Use Railway CLI Script (Recommended)

I've created a script that reads your local `.env` file and sets variables in Railway.

### Step 1: Install Railway CLI

```bash
npm i -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

### Step 3: Edit Your .env File

Make sure your `.env` file has all the values filled in:

```env
EMAIL_USER=your_actual_email@gmail.com
EMAIL_PASSWORD=your_actual_app_password
RECIPIENT_EMAIL=your_actual_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
HEADLESS=true
```

### Step 4: Run the Script

```bash
./set_railway_vars.sh
```

This will:
- Check if Railway CLI is installed
- Check if you're logged in
- Link your project (if needed)
- Read your `.env` file
- Set all variables in Railway
- Skip placeholder values

### Step 5: Verify

Check Railway logs - you should see "Email sent successfully" instead of "Email configuration missing".

## Method 2: Manual Railway CLI

If you prefer to set them manually:

```bash
# Login and link
railway login
railway link

# Set variables one by one
railway variables set EMAIL_USER=your_email@gmail.com
railway variables set EMAIL_PASSWORD=your_app_password
railway variables set RECIPIENT_EMAIL=your_email@gmail.com
railway variables set SMTP_SERVER=smtp.gmail.com
railway variables set SMTP_PORT=587
railway variables set HEADLESS=true
```

## Method 3: Railway Dashboard (Current Method)

You can continue using the Railway dashboard:
1. Go to your service → Variables tab
2. Add each variable manually

## Which Method to Use?

- **Method 1 (Script)**: Best if you want to manage variables locally and sync them
- **Method 2 (CLI)**: Good for quick updates
- **Method 3 (Dashboard)**: Easiest for one-time setup

## Troubleshooting

### "Railway CLI not found"
```bash
npm i -g @railway/cli
```

### "Not logged in"
```bash
railway login
```

### "Project not linked"
```bash
railway link
# Select your project when prompted
```

### Variables still not working

1. Check Railway logs for errors
2. Verify variables are set: `railway variables`
3. Make sure you're setting them on the correct service (not just project level)

## Security Best Practices

✅ **DO:**
- Keep `.env` in `.gitignore` (already done)
- Use Railway CLI to sync variables
- Use Gmail app passwords (not regular passwords)

❌ **DON'T:**
- Commit `.env` to git
- Share your `.env` file
- Use regular Gmail passwords

## Quick Reference

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project (first time)
railway link

# Set variables from .env file
./set_railway_vars.sh

# Or set manually
railway variables set KEY=value

# View all variables
railway variables
```

