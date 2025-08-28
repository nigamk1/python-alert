# Nifty 50 EMA Alerts - Netlify Deployment Guide

Deploy your Nifty 50 EMA alert system on Netlify with GitHub Actions for automated scheduling.

## 🚀 Why Netlify?

- **Simple Deployment**: Easy Python function deployment
- **Free Tier**: Generous limits for personal use
- **GitHub Integration**: Automatic deployments
- **Reliable Functions**: Built-in Python runtime
- **Easy Environment Variables**: Simple configuration

## 📋 Prerequisites

1. [Netlify Account](https://netlify.com) (free)
2. [GitHub Account](https://github.com) (free)
3. Your Upstox and Telegram API credentials

## 🛠️ Deployment Steps

### Step 1: Deploy to Netlify

#### Option A: Netlify Dashboard
1. Go to [Netlify Dashboard](https://app.netlify.com)
2. Click "New site from Git"
3. Connect to GitHub and select your `python-alert` repository
4. Configure build settings:
   - **Build command**: `echo 'No build required'`
   - **Publish directory**: `.`
   - **Functions directory**: `netlify/functions`

#### Option B: Netlify CLI
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy from your project directory
netlify deploy --prod
```

### Step 2: Configure Environment Variables

In Netlify Dashboard → Site Settings → Environment Variables, add:

```bash
UPSTOX_CLIENT_ID=your_upstox_client_id
UPSTOX_CLIENT_SECRET=your_upstox_client_secret
UPSTOX_REDIRECT_URI=https://your-site-name.netlify.app/.netlify/functions/auth
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
UPSTOX_ACCESS_TOKEN=<get_from_auth_endpoint>
```

### Step 3: One-Time Authentication

1. Visit: `https://your-site-name.netlify.app/.netlify/functions/auth`
2. Click "Login to Upstox"
3. Complete Upstox authentication
4. Copy the access token from the response
5. Add `UPSTOX_ACCESS_TOKEN` to Netlify environment variables

### Step 4: Setup GitHub Actions Cron (Automated Alerts)

1. In your GitHub repository, go to Settings → Secrets and Variables → Actions
2. Add this secret:
   - `NETLIFY_FUNCTION_URL`: `https://your-site-name.netlify.app/.netlify/functions`

3. The GitHub Action will automatically:
   - Run every 5 minutes during market hours (9:15 AM - 3:30 PM IST)
   - Call your Netlify function to check for alerts
   - Send Telegram notifications for bullish signals

### Step 5: Verify Deployment

- **Status Check**: `https://your-site-name.netlify.app/.netlify/functions/status`
- **Manual Alert**: `https://your-site-name.netlify.app/.netlify/functions/check_alerts`
- **Auth Setup**: `https://your-site-name.netlify.app/.netlify/functions/auth`

## ⚡ How It Works

### Architecture
```
GitHub Actions (Cron) → Netlify Functions → Upstox API → Telegram Bot
     ↓                        ↓                ↓            ↓
Every 5 minutes         Fetch Nifty 50     Calculate     Send Alert
during market hrs        & Calculate EMA      EMA Signal   if Bullish
```

### Function Endpoints

| Function | URL | Purpose |
|----------|-----|---------|
| `status` | `/.netlify/functions/status` | System status check |
| `auth` | `/.netlify/functions/auth` | One-time authentication |
| `check_alerts` | `/.netlify/functions/check_alerts` | Check market & send alerts |

## 🔧 GitHub Actions Schedule

The cron job runs:
- **Frequency**: Every 5 minutes
- **Time**: 9:15 AM - 3:30 PM IST (Monday-Friday)
- **Trigger**: Automatically calls Netlify function
- **Manual**: Can be triggered manually from GitHub Actions tab

## 📱 Sample Alert Message

```
🟢 BULLISH ALERT - Nifty 50

📅 Time: 2025-08-28 14:30:00
📈 Close: ₹24,710.70
📊 EMA(5): ₹24,690.25

💡 Signal: Candle is fully above EMA
🎯 Trend: Bullish momentum detected

Automated alert from Netlify deployment
```

## 🔄 Token Management

### When Access Token Expires:
1. You'll receive error notifications in Telegram
2. Visit: `https://your-site-name.netlify.app/.netlify/functions/auth`
3. Get new access token
4. Update `UPSTOX_ACCESS_TOKEN` in Netlify environment variables

## 📊 Monitoring & Troubleshooting

### Check Function Logs:
1. Netlify Dashboard → Functions → View logs
2. GitHub Actions → Check workflow runs
3. Telegram error notifications

### Test Endpoints:
```bash
# Test status
curl https://your-site-name.netlify.app/.netlify/functions/status

# Test manual alert
curl https://your-site-name.netlify.app/.netlify/functions/check_alerts
```

### Common Issues:

1. **Function Cold Starts**: First request might be slow
2. **Timeout**: Functions timeout after 10 seconds
3. **Import Errors**: Check function logs for Python package issues

## 🎯 Benefits of Netlify + GitHub Actions

### ✅ Advantages:
- **Reliable**: Battle-tested infrastructure
- **Free**: No costs for personal use
- **Scalable**: Automatic scaling
- **Simple**: Easy setup and maintenance
- **Flexible**: Easy to modify and update

### 🔄 vs Vercel:
- **Better Python Support**: Native Python runtime
- **Simpler Config**: Less configuration required
- **GitHub Actions**: More flexible scheduling
- **Better Logs**: Easier debugging

## 🚀 Deployment Commands

### Quick Deploy:
```bash
# Clone repository
git clone https://github.com/nigamk1/python-alert.git
cd python-alert

# Deploy to Netlify
netlify deploy --prod

# Set environment variables in Netlify dashboard
# Visit auth endpoint for one-time setup
# Add NETLIFY_FUNCTION_URL to GitHub secrets
```

## 📈 Future Enhancements

- [ ] Web dashboard interface
- [ ] Multiple timeframe alerts
- [ ] Portfolio integration
- [ ] Advanced indicators (RSI, MACD)
- [ ] Multiple stock monitoring
- [ ] Database storage for alert history

## 🎉 You're All Set!

Once deployed:
1. **Automatic Monitoring**: GitHub Actions calls your function every 5 minutes
2. **Bullish Alerts**: Receive Telegram notifications for opportunities
3. **Lifetime Service**: Runs continuously with minimal maintenance
4. **Professional Setup**: Scalable, reliable, and free!

---

**Your Nifty 50 EMA alert system will now run 24/7 on Netlify! 🚀📈**
