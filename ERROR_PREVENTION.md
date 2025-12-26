# Error Prevention Guide - Railway Deployment

## Pre-Deployment Checklist

### 1. Environment Variables ✅
**Critical**: These MUST be set in Railway dashboard before first deployment:

```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password  # NOT regular password!
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
HEADLESS=true  # Required for Railway
```

**Test locally first:**
```bash
# Verify .env file has all variables
cat .env | grep -E "EMAIL_|SMTP_|HEADLESS"
```

### 2. Docker Build Test ✅
**Test Docker build locally** (simulates Railway exactly):

```bash
# Build the Docker image (same as Railway will)
docker build -t reverseweave-test .

# If build succeeds, you're good!
```

### 3. Code Validation ✅
**Run pre-deployment check:**
```bash
python3 pre_deployment_check.py
```

### 4. Common Error Prevention

#### A. Missing Environment Variables
**Error**: `KeyError` or `None` values
**Prevention**: 
- ✅ All env vars documented in `env_template.txt`
- ✅ Code uses `os.getenv()` with defaults where appropriate
- ⚠️ **Action**: Double-check Railway Variables tab

#### B. ChromeDriver Issues
**Error**: `chromedriver not found` or `Exec format error`
**Prevention**:
- ✅ Dockerfile installs ChromeDriver correctly
- ✅ Code has fallback to ChromeDriverManager
- ✅ Linux-specific paths in Dockerfile
- ⚠️ **Action**: Railway uses Linux, so local Mac issues won't occur

#### C. Database Permissions
**Error**: `Permission denied` writing to database
**Prevention**:
- ✅ Database file created in `/app` directory (writable)
- ✅ No volume mounts needed (SQLite works in container)
- ⚠️ **Action**: Railway handles this automatically

#### D. Email Sending Failures
**Error**: `SMTPAuthenticationError` or `Connection refused`
**Prevention**:
- ✅ Code checks for env vars before sending
- ✅ Uses Gmail app password (not regular password)
- ⚠️ **Action**: Verify Gmail app password is correct

#### E. Import Errors
**Error**: `ModuleNotFoundError`
**Prevention**:
- ✅ All dependencies in `requirements.txt`
- ✅ Dockerfile installs from requirements.txt
- ⚠️ **Action**: Verify `requirements.txt` is up to date

### 5. Railway-Specific Considerations

#### Memory Limits
- Railway free tier: 512MB RAM
- Selenium + Chrome needs ~300-400MB
- ✅ Your code should work fine
- ⚠️ **Monitor**: Check Railway metrics if issues occur

#### Timeout Limits
- Railway has request timeouts
- Your bot runs continuously (not web requests)
- ✅ Should be fine
- ⚠️ **Action**: If timeouts occur, check Railway plan limits

#### Logging
- ✅ All errors logged to `champion_monitor.log`
- ✅ Railway captures stdout/stderr
- ⚠️ **Action**: Check Railway logs tab for errors

## Testing Docker Build (Railway Simulation)

Run this to test exactly what Railway will do:

```bash
# Build Docker image
docker build -t reverseweave-test .

# Test run (with env vars)
docker run --rm \
  -e EMAIL_USER=test@example.com \
  -e EMAIL_PASSWORD=test \
  -e RECIPIENT_EMAIL=test@example.com \
  -e SMTP_SERVER=smtp.gmail.com \
  -e SMTP_PORT=587 \
  -e HEADLESS=true \
  reverseweave-test

# If it starts without errors, Railway will work!
```

## Monitoring After Deployment

### Railway Dashboard
1. **Logs Tab**: Real-time logs (like `champion_monitor.log`)
2. **Metrics Tab**: CPU, Memory, Network usage
3. **Variables Tab**: Verify all env vars are set

### What to Look For

✅ **Good Signs:**
- Logs show "Starting monitoring cycle"
- Logs show "Checking eBay..." and "Checking Depop..."
- No error messages
- Service status is "Active"

❌ **Warning Signs:**
- "Driver not initialized" errors
- "Email configuration missing" errors
- "ModuleNotFoundError" errors
- Service keeps restarting

## Quick Fixes After Deployment

See `QUICK_FIXES.md` for common issues and solutions.

