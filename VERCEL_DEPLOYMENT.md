# Nifty 50 EMA Alerts - Vercel Deployment Guide

This guide explains how to deploy your Nifty 50 EMA alert system on Vercel for lifetime alerts with one-time setup.

## 🚀 Vercel Deployment Benefits

- **Serverless**: No server management required
- **Automatic Scaling**: Handles traffic automatically
- **Cron Jobs**: Built-in scheduled function execution
- **One-time Setup**: Configure once, run forever
- **Free Tier**: Generous free limits for personal use

## 📋 Prerequisites

1. [Vercel Account](https://vercel.com) (free)
2. [GitHub Account](https://github.com) (free)
3. Your Upstox and Telegram API credentials

## 🛠️ Deployment Steps

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Clone Your Repository

```bash
git clone https://github.com/nigamk1/python-alert.git
cd python-alert
```

### Step 3: Configure Environment Variables

In your Vercel dashboard or using CLI, set these environment variables:

```bash
# Upstox Configuration
UPSTOX_CLIENT_ID=your_upstox_client_id
UPSTOX_CLIENT_SECRET=your_upstox_client_secret
UPSTOX_REDIRECT_URI=https://your-app-name.vercel.app/api/auth

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Access Token (set after initial authentication)
UPSTOX_ACCESS_TOKEN=your_access_token
```

### Step 4: Deploy to Vercel

```bash
vercel --prod
```

### Step 5: One-Time Authentication

1. Visit: `https://your-app-name.vercel.app/api/auth`
2. Click "Login to Upstox"
3. Complete Upstox authentication
4. Copy the access token from the response
5. Add the token to your Vercel environment variables:
   ```bash
   vercel env add UPSTOX_ACCESS_TOKEN
   ```

### Step 6: Verify Deployment

- Check status: `https://your-app-name.vercel.app/api/status`
- Manual alert check: `https://your-app-name.vercel.app/api/check_alerts`

## ⚡ How It Works

### Cron Job (Automatic)
- Vercel runs `/api/check_alerts` every 5 minutes
- Fetches Nifty 50 data and calculates EMA
- Sends Telegram alerts for bullish signals

### API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/api/status` | System status check |
| `/api/auth` | One-time Upstox authentication |
| `/api/check_alerts` | Manual alert check (also runs via cron) |

## 🔧 Environment Variables Setup

### Via Vercel Dashboard:
1. Go to your project dashboard
2. Settings → Environment Variables
3. Add each variable with its value

### Via Vercel CLI:
```bash
vercel env add UPSTOX_CLIENT_ID
vercel env add UPSTOX_CLIENT_SECRET
vercel env add UPSTOX_REDIRECT_URI
vercel env add TELEGRAM_BOT_TOKEN
vercel env add TELEGRAM_CHAT_ID
vercel env add UPSTOX_ACCESS_TOKEN
```

## 📱 Sample Alert Message

```
🟢 BULLISH ALERT - Nifty 50

📅 Time: 2025-08-28 14:30:00
📈 Close: ₹24,710.70
📊 EMA(5): ₹24,690.25

💡 Signal: Candle is fully above EMA
🎯 Trend: Bullish momentum detected

Automated alert from Vercel deployment
```

## 🔄 Token Management

### Access Token Expiry
- Upstox access tokens typically expire after 24 hours
- When expired, you'll get error notifications in Telegram
- Simply re-visit `/api/auth` to get a new token
- Update the `UPSTOX_ACCESS_TOKEN` environment variable

### Automatic Token Refresh (Future Enhancement)
- Could implement automatic token refresh using Vercel KV
- Store refresh token securely
- Auto-refresh before expiry

## 📊 Monitoring

### Success Indicators:
- Regular status updates in Telegram
- No error messages
- `/api/status` returns "running"

### Troubleshooting:
- Check Vercel function logs
- Verify environment variables
- Test individual endpoints
- Check Telegram bot status

## 🎯 Benefits of This Architecture

1. **No Server Costs**: Runs on Vercel's free tier
2. **Automatic Scaling**: Handles any load
3. **Reliable Cron**: Built-in scheduling
4. **Easy Updates**: Git push to deploy
5. **Monitoring**: Built-in logs and metrics

## 🔮 Future Enhancements

- [ ] Automatic token refresh
- [ ] Multiple stock support
- [ ] Web dashboard
- [ ] Database integration (Vercel KV/PostgreSQL)
- [ ] Multiple alert strategies
- [ ] User management for multiple users

## 🚨 Important Notes

- Free Vercel tier has execution limits (check current limits)
- Functions timeout after 10 seconds (hobby plan)
- Environment variables are encrypted and secure
- Cron jobs may have slight delays (±1 minute)

## 📞 Support

- Check Vercel documentation for deployment issues
- Monitor function logs in Vercel dashboard
- Test endpoints manually if needed

---

**Your Nifty 50 EMA alert system will now run 24/7 on Vercel with minimal maintenance! 🚀📈**
