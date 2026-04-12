# Railway Deployment Guide

## Prerequisites
- Railway account
- GitHub repository with the bot code
- Telegram Bot Token

## Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect the Dockerfile and deploy

### 3. Environment Variables
Set the following environment variable in Railway dashboard:
- `BOT_TOKEN`: Your Telegram bot token

### 4. Configuration
The bot is configured with:
- Health check endpoint: `/health` on port 8000
- Download directory: `/tmp/downloads` (ephemeral storage)
- Restart policy: On failure with max 10 retries
- Health check timeout: 100 seconds

### 5. Monitoring
- Health checks are automatically configured
- Logs are available in Railway dashboard
- The bot will restart automatically on crashes

## Files Created/Modified
- `railway.toml`: Railway configuration
- `health_server.py`: Health check endpoint
- `Dockerfile`: Updated for Railway compatibility
- `config.py`: Updated download directory path
- `bot.py`: Added health server integration

## Troubleshooting
- Ensure BOT_TOKEN is set correctly
- Check logs in Railway dashboard
- Verify health check is responding: `https://your-app.railway.app/health`
