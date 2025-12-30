# Email Setup Guide - Fixing Railway Network Issues

## Problem
Railway blocks outbound SMTP connections (ports 587 and 465), causing email sending to fail with `Network is unreachable` errors.

## Solution: Use Resend API

Resend is an email API service that uses HTTP (not SMTP), so it works perfectly with Railway's network restrictions.

### Why Resend?
- ✅ Works with Railway (uses HTTP, not SMTP)
- ✅ Free tier: 3,000 emails/month, 100 emails/day
- ✅ Easy setup (just an API key)
- ✅ Reliable delivery
- ✅ No need for app passwords

## Setup Steps

### 1. Create Resend Account
1. Go to https://resend.com
2. Sign up for a free account
3. Verify your email address

### 2. Get Your API Key
1. Go to https://resend.com/api-keys
2. Click "Create API Key"
3. Name it (e.g., "Vintage Bot")
4. Copy the API key (starts with `re_`)

### 3. Verify Your Domain (Optional but Recommended)
For better deliverability:
1. Go to https://resend.com/domains
2. Click "Add Domain"
3. Follow DNS setup instructions
4. Use your verified domain in `RESEND_FROM_EMAIL`

**OR** use Resend's default domain:
- From email: `onboarding@resend.dev` (works immediately, no verification needed)

### 4. Set Railway Environment Variables

Add these to your Railway project:

```bash
# Required
RESEND_API_KEY=re_your_api_key_here
RECIPIENT_EMAIL=your_email@gmail.com

# Optional (if using custom domain)
RESEND_FROM_EMAIL=notifications@yourdomain.com

# Optional (fallback to SMTP if Resend fails)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 5. Set Variables via Railway Dashboard
1. Go to Railway dashboard
2. Select your project
3. Go to "Variables" tab
4. Click "New Variable"
5. Add:
   - `RESEND_API_KEY` = `re_your_key_here`
   - `RECIPIENT_EMAIL` = `your_email@gmail.com`
   - `RESEND_FROM_EMAIL` = `onboarding@resend.dev` (or your verified domain)

### 6. Set Variables via CLI (Alternative)
```bash
railway variables set RESEND_API_KEY=re_your_key_here
railway variables set RECIPIENT_EMAIL=your_email@gmail.com
railway variables set RESEND_FROM_EMAIL=onboarding@resend.dev
```

## How It Works

The bot will:
1. **First try Resend API** (works with Railway)
2. **Fallback to SMTP** if Resend fails (may not work on Railway)

## Testing

After setting variables, the bot will automatically use Resend on the next monitoring cycle. Check logs for:
```
Email sent successfully via Resend API with X listings
```

## Troubleshooting

### "Resend API failed"
- Check that `RESEND_API_KEY` is set correctly
- Verify the API key starts with `re_`
- Check Resend dashboard for any errors

### "Email configuration missing"
- Make sure `RESEND_API_KEY` and `RECIPIENT_EMAIL` are set
- Check Railway variables are saved correctly

### Still using SMTP?
- The bot falls back to SMTP if Resend fails
- Check logs to see which method is being used
- If SMTP is being used, Resend setup may be incomplete

## Cost

- **Free tier**: 3,000 emails/month, 100/day
- **Paid**: $20/month for 50,000 emails
- Perfect for monitoring bot (sends ~30 emails/day max)

## Alternative: SendGrid

If you prefer SendGrid:
1. Sign up at https://sendgrid.com
2. Get API key
3. Use `SENDGRID_API_KEY` environment variable
4. (Code modification needed - let me know if you want this)

## Questions?

Check Resend docs: https://resend.com/docs

