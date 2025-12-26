# Cloud Deployment Guide

This guide will help you deploy the Champion Reverse Weave Monitor Bot to various cloud platforms, eliminating the need for a Raspberry Pi.

## Why Deploy to Cloud?

- ✅ **No hardware setup** - No need for Raspberry Pi, cables, or WiFi configuration
- ✅ **Always running** - Cloud services run 24/7 without interruption
- ✅ **Easy updates** - Update code from anywhere via Git
- ✅ **Better reliability** - Cloud platforms have better uptime than home networks
- ✅ **Remote access** - Monitor and manage from anywhere

## Platform Options

### Recommended Platforms (Easiest)

1. **Railway** ⭐ (Recommended)
   - Free tier: $5/month credit
   - Easy Docker deployment
   - Automatic HTTPS
   - Simple Git integration
   - **Cost**: ~$5-10/month after free credit

2. **Render**
   - Free tier available (with limitations)
   - Easy deployment
   - Automatic HTTPS
   - **Cost**: Free tier or ~$7/month for always-on

3. **Fly.io**
   - Generous free tier
   - Global deployment
   - Docker-based
   - **Cost**: Free tier or ~$5/month

### Alternative Platforms

4. **DigitalOcean App Platform**
   - Simple deployment
   - Good documentation
   - **Cost**: ~$5-12/month

5. **AWS EC2/Lightsail**
   - More control
   - Requires more setup
   - **Cost**: ~$3.50-10/month

6. **Google Cloud Run**
   - Serverless option
   - Pay per use
   - **Cost**: Very cheap for low usage

---

## Option 1: Railway (Recommended) 🚂

Railway is the easiest option with great free credits and simple deployment.

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project

### Step 2: Deploy from GitHub

1. **Push your code to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **In Railway dashboard**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect the Dockerfile

### Step 3: Configure Environment Variables

In Railway dashboard, go to your service → Variables tab, add:

```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Step 4: Deploy

Railway will automatically:
- Build the Docker image
- Deploy your service
- Keep it running 24/7

### Step 5: Monitor

- View logs in Railway dashboard
- Check service status
- Monitor resource usage

**Cost**: ~$5-10/month after free $5 credit

---

## Option 2: Render 🌐

Render offers a free tier with some limitations, or a paid tier for always-on services.

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Create New Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Render will auto-detect Dockerfile

### Step 3: Configure

- **Name**: champion-monitor
- **Environment**: Docker
- **Plan**: Free (or Starter for always-on)

### Step 4: Add Environment Variables

In the Environment tab, add:

```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Step 5: Deploy

Click "Create Web Service" and Render will deploy.

**Note**: Free tier services spin down after 15 minutes of inactivity. For always-on, use Starter plan ($7/month).

**Cost**: Free (with spin-down) or $7/month (always-on)

---

## Option 3: Fly.io ✈️

Fly.io has a generous free tier and global deployment.

### Step 1: Install Fly CLI

```bash
# macOS
curl -L https://fly.io/install.sh | sh

# Or download from https://fly.io/docs/hands-on/install-flyctl/
```

### Step 2: Sign Up

```bash
fly auth signup
```

### Step 3: Deploy

```bash
# In your project directory
fly launch

# Follow prompts:
# - App name: champion-monitor (or your choice)
# - Region: Choose closest to you
# - Postgres: No
# - Redis: No
```

### Step 4: Set Environment Variables

```bash
fly secrets set EMAIL_USER=your_email@gmail.com
fly secrets set EMAIL_PASSWORD=your_app_password
fly secrets set RECIPIENT_EMAIL=your_email@gmail.com
fly secrets set SMTP_SERVER=smtp.gmail.com
fly secrets set SMTP_PORT=587
```

### Step 5: Deploy

```bash
fly deploy
```

### Step 6: Monitor

```bash
# View logs
fly logs

# Check status
fly status
```

**Cost**: Free tier (3 shared-cpu-1x VMs) or ~$5/month for dedicated

---

## Option 4: DigitalOcean App Platform 💧

### Step 1: Create Account

1. Go to [digitalocean.com](https://www.digitalocean.com)
2. Sign up (get $200 credit with referral)

### Step 2: Create App

1. Go to App Platform
2. Click "Create App"
3. Connect GitHub repository
4. Select Dockerfile

### Step 3: Configure

- **Plan**: Basic ($5/month) or Professional
- Add environment variables (same as above)

### Step 4: Deploy

Click "Create Resources" to deploy.

**Cost**: $5-12/month

---

## Option 5: AWS EC2 (More Control) ☁️

For more control and lower cost, use EC2.

### Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2
2. Launch Instance
3. Choose: Ubuntu 22.04 LTS
4. Instance type: t2.micro (free tier) or t3.micro
5. Configure security group (allow SSH)
6. Launch

### Step 2: Connect via SSH

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 3: Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Log out and back in, or:
newgrp docker
```

### Step 4: Clone and Run

```bash
# Clone your repo
git clone <your-repo-url> champion-monitor
cd champion-monitor

# Create .env file
nano .env
# Add your environment variables

# Run with Docker
docker build -t champion-monitor .
docker run -d --name champion-monitor --env-file .env --restart unless-stopped champion-monitor

# Or use docker-compose (see below)
```

### Step 5: Set Up Auto-Start

Docker's `--restart unless-stopped` flag will auto-start on reboot.

**Cost**: Free tier (t2.micro) or ~$3.50-10/month

---

## Docker Compose (Optional)

For easier management, create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  champion-monitor:
    build: .
    container_name: champion-monitor
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./champion_listings.db:/app/champion_listings.db
      - ./logs:/app/logs
```

Run with:
```bash
docker-compose up -d
```

---

## Environment Variables

All platforms need these environment variables:

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Gmail App Password Setup

1. Enable 2-factor authentication on Gmail
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Generate password for "Mail"
4. Use this password (not your regular password) in `EMAIL_PASSWORD`

---

## Database Persistence

The SQLite database (`champion_listings.db`) needs to persist between restarts.

### Railway/Render/Fly.io
- Use volumes (configured in Dockerfile)
- Or use external database (PostgreSQL) for production

### EC2/DigitalOcean
- Use Docker volumes (configured in docker-compose.yml)
- Or mount host directory

---

## Monitoring and Logs

### Railway
- View logs in dashboard
- Set up alerts for errors

### Render
- View logs in dashboard
- Set up webhooks for notifications

### Fly.io
```bash
fly logs
fly status
```

### EC2
```bash
# View Docker logs
docker logs champion-monitor -f

# Or view application logs
tail -f champion_monitor.log
```

---

## Updating the Bot

### Railway/Render/Fly.io
Just push to GitHub - they auto-deploy:

```bash
git add .
git commit -m "Update bot"
git push
```

### EC2
```bash
# SSH into instance
ssh ubuntu@your-ec2-ip

# Pull latest code
cd champion-monitor
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## Troubleshooting

### Bot Not Running

1. **Check logs**:
   - Railway/Render: Dashboard logs
   - Fly.io: `fly logs`
   - EC2: `docker logs champion-monitor`

2. **Check environment variables**:
   - Ensure all required vars are set
   - Verify Gmail app password is correct

3. **Check resources**:
   - Ensure service has enough memory (512MB+)
   - Selenium needs Chrome, which uses memory

### Email Not Sending

1. Verify Gmail app password (not regular password)
2. Check SMTP settings
3. Check logs for email errors
4. Test with simple Python script

### Selenium Issues

1. Ensure Chrome/Chromium is installed (handled by Dockerfile)
2. Check for headless mode errors
3. Verify ChromeDriver version matches Chrome

### Database Issues

1. Ensure database file has write permissions
2. Check volume mounts are correct
3. Backup database regularly

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| Railway | $5 credit | $5-10/mo | Easiest setup |
| Render | Limited | $7/mo | Simple deployment |
| Fly.io | Generous | $5/mo | Global, flexible |
| DigitalOcean | None | $5-12/mo | Simple, reliable |
| AWS EC2 | Free tier | $3.50-10/mo | Most control |

---

## Recommendation

**For easiest setup**: Use **Railway** - it's the simplest with good free credits.

**For free option**: Use **Fly.io** - generous free tier.

**For most control**: Use **AWS EC2** - full control, lowest cost.

---

## Next Steps

1. Choose a platform
2. Push code to GitHub
3. Follow platform-specific steps above
4. Set environment variables
5. Deploy!
6. Monitor logs to ensure it's working

Your bot will now run 24/7 in the cloud! 🎉

