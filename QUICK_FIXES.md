# Quick Fixes - Railway Deployment Issues

## How Easy Is It to Update Files?

**Very Easy!** Railway auto-deploys from GitHub:

1. **Make changes locally**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Fix: description of fix"
   git push
   ```
3. **Railway automatically:**
   - Detects the push
   - Rebuilds Docker image
   - Redeploys service
   - Usually takes 2-5 minutes

**No manual deployment needed!** Just push to GitHub.

## Common Issues & Quick Fixes

### Issue 1: "Driver not initialized"

**Symptoms:**
- Logs show "Driver not initialized"
- No listings found
- Service running but not scraping

**Quick Fix:**
1. Check Railway logs for ChromeDriver errors
2. If ChromeDriver issue, update Dockerfile ChromeDriver installation
3. Push fix:
   ```bash
   git add Dockerfile
   git commit -m "Fix: Update ChromeDriver installation"
   git push
   ```

**Prevention:** Already handled in Dockerfile ✅

---

### Issue 2: "Email configuration missing"

**Symptoms:**
- Logs show "Email configuration missing"
- No emails sent

**Quick Fix:**
1. Go to Railway dashboard → Variables tab
2. Verify all required variables are set:
   - `EMAIL_USER`
   - `EMAIL_PASSWORD` (Gmail app password!)
   - `RECIPIENT_EMAIL`
   - `SMTP_SERVER`
   - `SMTP_PORT`
3. No code changes needed - just set variables

**Prevention:** Check variables before first deployment ✅

---

### Issue 3: "ModuleNotFoundError: No module named 'X'"

**Symptoms:**
- Service fails to start
- Import errors in logs

**Quick Fix:**
1. Add missing module to `requirements.txt`:
   ```bash
   echo "missing-module==1.0.0" >> requirements.txt
   ```
2. Commit and push:
   ```bash
   git add requirements.txt
   git commit -m "Fix: Add missing dependency"
   git push
   ```

**Prevention:** All dependencies already in requirements.txt ✅

---

### Issue 4: Service Keeps Restarting

**Symptoms:**
- Service status shows restarting
- Logs show crash loop

**Quick Fix:**
1. Check Railway logs for error message
2. Common causes:
   - Missing environment variable
   - Import error
   - ChromeDriver issue
3. Fix the root cause and push

**Debug:**
```bash
# Check logs in Railway dashboard
# Look for the last error before restart
```

---

### Issue 5: "No listings found" (but should find some)

**Symptoms:**
- Bot runs but finds 0 listings
- Logs show searches but no results

**Possible Causes:**
1. **Search terms too specific** - Normal, no fix needed
2. **Scraper blocked** - Check if eBay/Depop changed structure
3. **Driver issues** - Check logs for Selenium errors

**Quick Fix:**
1. Check Railway logs for scraping errors
2. Test search terms manually on eBay/Depop
3. If site structure changed, update selectors in scrapers
4. Push fix:
   ```bash
   git add ebay_selenium_scraper.py depop_selenium_scraper.py
   git commit -m "Fix: Update selectors for site changes"
   git push
   ```

---

### Issue 6: Database Permission Errors

**Symptoms:**
- "Permission denied" writing to database
- Database file not created

**Quick Fix:**
1. Railway handles this automatically
2. If issue persists, check Railway logs
3. May need to adjust file paths in code

**Prevention:** Already handled - database in `/app` directory ✅

---

### Issue 7: Memory/Resource Issues

**Symptoms:**
- Service crashes
- "Out of memory" errors
- Slow performance

**Quick Fix:**
1. Check Railway Metrics tab
2. If memory usage high:
   - Upgrade Railway plan
   - Or optimize code (reduce concurrent searches)
3. Update code if needed:
   ```bash
   # Make changes to reduce memory usage
   git add .
   git commit -m "Fix: Reduce memory usage"
   git push
   ```

---

## Emergency Rollback

If something breaks badly:

1. **Revert to previous commit:**
   ```bash
   git revert HEAD
   git push
   ```

2. **Or rollback in Railway:**
   - Railway dashboard → Deployments tab
   - Click on previous working deployment
   - Click "Redeploy"

## Testing Fixes Locally

Before pushing fixes, test locally:

```bash
# Test Docker build
docker build -t reverseweave-test .

# Test with same env as Railway
docker run --rm \
  -e HEADLESS=true \
  -e EMAIL_USER=test@example.com \
  reverseweave-test
```

## Best Practices

1. **Test locally first** - Use Docker to simulate Railway
2. **Check logs immediately** - Railway logs update in real-time
3. **Small, incremental changes** - Easier to debug
4. **Monitor after deployment** - Watch logs for first 10 minutes
5. **Keep backups** - Git history is your backup

## Getting Help

If you can't fix an issue:

1. **Check Railway logs** - Most errors are visible there
2. **Check this guide** - Common issues covered
3. **Test locally with Docker** - Reproduce issue locally
4. **Check GitHub issues** - For dependency-related issues

## Update Frequency

**Typical update cycle:**
- Push code → Railway detects → Builds (1-2 min) → Deploys (1-2 min)
- **Total: 2-5 minutes** from push to live

**Very easy to iterate!** Just push to GitHub.

