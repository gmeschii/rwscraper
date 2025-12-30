# Email Sending Fix for Railway

## Problem
The bot was getting `[Errno 101] Network is unreachable` when trying to send emails on Railway.

## Solution
Updated email sending code to:
1. **Try port 587 (STARTTLS) first** - Standard Gmail SMTP
2. **Fall back to port 465 (SSL)** - More reliable on Railway's network
3. **Added timeout (30 seconds)** - Prevents hanging
4. **Better error handling** - Logs which method failed

## What Changed
- Email code now automatically tries both ports
- If port 587 fails, it tries port 465 with SSL
- More reliable on Railway's network infrastructure

## No Action Needed
The fix is automatic! The bot will:
- Try port 587 first (your current setting)
- If that fails, automatically try port 465
- Log which method worked

## Optional: Use Port 465 Directly
If you want to skip the retry and use SSL directly, update your Railway variable:

```
SMTP_PORT=465
```

But the automatic fallback should work fine!

## Testing
After Railway redeploys, check the logs:
- ✅ `Email sent successfully with X listings` - Success!
- ✅ `Email sent successfully with X listings (via SSL)` - Success via fallback!
- ❌ `Failed to send email` - Check your Gmail app password

## Gmail App Password
Make sure you're using a **Gmail App Password**, not your regular password:
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Generate App Password
4. Use that 16-character password in `EMAIL_PASSWORD`

