# How to Set Environment Variables in Railway

## Finding the Variables Tab

The Variables tab location depends on Railway's UI version. Here are all the ways to access it:

### Method 1: Service Settings (Most Common)

1. In Railway dashboard, click on your **service** (the box with your project name)
2. Look for tabs at the top: **Variables**, **Settings**, **Deployments**, **Logs**, **Metrics**
3. Click on **"Variables"** tab

### Method 2: Service Menu

1. Click on your service
2. Look for a **gear icon** ⚙️ or **"Settings"** button
3. Click it → You'll see **"Variables"** option

### Method 3: Three Dots Menu

1. Click on your service
2. Look for **three dots** (⋯) or **"More"** menu
3. Click it → Select **"Variables"** or **"Environment Variables"**

### Method 4: Direct URL

If you know your service ID, you can go directly to:
```
https://railway.app/project/[PROJECT_ID]/service/[SERVICE_ID]/variables
```

### Method 5: Project Settings

1. Click on your **project name** (not the service)
2. Look for **"Variables"** in the project settings
3. Note: Project-level variables apply to all services

## What You Should See

Once you find the Variables tab, you should see:
- A list of existing variables (if any)
- A **"New Variable"** or **"Add Variable"** button
- Fields for **Name** and **Value**

## Adding Variables

1. Click **"New Variable"** or **"Add Variable"**
2. Enter the variable name (e.g., `EMAIL_USER`)
3. Enter the value (e.g., `your_email@gmail.com`)
4. Click **"Add"** or **"Save"**
5. Repeat for all 6 variables

## Required Variables

Add these 6 variables:

```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=your_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
HEADLESS=true
```

## If You Still Can't Find It

1. **Check Railway's documentation**: https://docs.railway.app/develop/variables
2. **Try the new UI**: Railway sometimes has a "New UI" toggle
3. **Contact Railway support**: They can help you locate it
4. **Alternative**: Use Railway CLI to set variables (see below)

## Using Railway CLI (Alternative Method)

If you can't find the Variables tab, you can use Railway CLI:

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Link to your project**:
   ```bash
   railway link
   ```

4. **Set variables**:
   ```bash
   railway variables set EMAIL_USER=your_email@gmail.com
   railway variables set EMAIL_PASSWORD=your_app_password
   railway variables set RECIPIENT_EMAIL=your_email@gmail.com
   railway variables set SMTP_SERVER=smtp.gmail.com
   railway variables set SMTP_PORT=587
   railway variables set HEADLESS=true
   ```

## Visual Guide

The Variables tab is usually:
- **Top of the page** - As a tab next to "Deployments", "Logs", "Metrics"
- **Left sidebar** - In some Railway UI versions
- **Settings menu** - Under service settings

Look for these keywords:
- "Variables"
- "Environment Variables"
- "Env Vars"
- "Secrets" (sometimes variables are called secrets)

## Still Having Trouble?

Take a screenshot of your Railway dashboard and I can help you locate it!

