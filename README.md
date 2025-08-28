# Nifty 50 EMA Alerts with Upstox + Telegram

A Python-based automated trading alert system that monitors Nifty 50 index using Upstox API and sends real-time EMA-based signals to Telegram. Deployed on Netlify with GitHub Actions for lifetime alerts.

## 🚀 Features

- **Real-time Monitoring**: Fetches live Nifty 50 data using 1-minute intervals, converted to 5-minute candles
- **EMA Analysis**: Calculates Exponential Moving Average (default: EMA 5)
- **Smart Alerts**: Sends Telegram notifications for bullish signals only
- **Duplicate Prevention**: Avoids sending repeated alerts for the same signal
- **Automated Scheduling**: GitHub Actions trigger alerts every 5 minutes during market hours
- **One-Time Setup**: Configure once, receive lifetime alerts
- **Serverless**: Runs on Netlify Functions with zero maintenance

## ⚠️ Important Notes About Upstox API

1. **Data Intervals**: Upstox API only supports: `1minute`, `30minute`, `day`, `week`, `month`
2. **5-Minute Candles**: The system fetches 1-minute data and converts it to 5-minute candles
3. **Token Management**: Upstox provides access tokens (not refresh tokens), so re-authentication is needed when tokens expire
4. **Market Hours**: System works during market hours (9:15 AM - 3:30 PM IST)

## 📁 Project Structure

```
Python/
├── main.py                 # Main script - local development & testing
├── auth.py                 # Handles Upstox authentication & token management
├── upstox_client.py        # Upstox API wrapper for data fetching & EMA calculation
├── telegram_bot.py         # Telegram bot for sending alerts
├── netlify/
│   └── functions/          # Netlify serverless functions
│       ├── check_alerts.py # Main monitoring function
│       ├── auth.py         # Authentication endpoint
│       ├── status.py       # Health check endpoint
│       └── requirements.txt # Python dependencies
├── .github/
│   └── workflows/
│       └── cron-alerts.yml # GitHub Actions cron job
├── config.json             # Configuration file for API keys (local only)
├── config.sample.json      # Template for API configuration
├── netlify.toml            # Netlify configuration
├── requirements.txt        # Python dependencies
├── NETLIFY_DEPLOYMENT.md   # Deployment guide
└── README.md              # This file
```

## 🛠️ Setup Instructions

### Step 1: Install Dependencies

```bash
pip install pandas numpy requests
```

### Step 2: Get API Credentials

#### Upstox API:
1. Sign up at [Upstox Developer Console](https://developer.upstox.com/)
2. Create a new app to get:
   - `client_id`
   - `client_secret`
   - Set `redirect_uri` to `http://localhost:5000/callback`

#### Telegram Bot:
1. Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. Get your `bot_token`
3. Get your `chat_id` by messaging [@userinfobot](https://t.me/userinfobot)

### Step 3: Configure API Keys

Copy the sample config file and edit it with your credentials:

```bash
cp config.sample.json config.json
```

Then edit `config.json` with your actual credentials:

```json
{
  "upstox": {
    "client_id": "YOUR_UPSTOX_CLIENT_ID",
    "client_secret": "YOUR_UPSTOX_CLIENT_SECRET",
    "redirect_uri": "http://localhost:5000/callback"
  },
  "telegram": {
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "chat_id": "YOUR_TELEGRAM_CHAT_ID"
  }
}
```

**⚠️ Important:** Never commit `config.json` to git as it contains sensitive API keys!

### Step 4: First-Time Authentication

Run the authentication script:

```bash
python auth.py
```

**What happens:**
1. Opens Upstox login URL in your browser
2. After login, you'll be redirected to a callback URL
3. Copy the complete redirect URL and paste it into the console
4. Script exchanges the code for access token and refresh token
5. Saves refresh token to `upstox_refresh.json`

**Example redirect URL:**
```
http://localhost:5000/callback?code=YOUR_REQUEST_TOKEN&state=
```

### Step 5: Start Monitoring

```bash
python main.py
```

## 📊 Alert Logic

### Bullish Signal 🟢
- **Condition**: Current 5-minute candle is fully above EMA (both low and high > EMA)
- **Action**: Sends "Bullish Alert" to Telegram

### Bearish Signal 🔴
- **Condition**: Current 5-minute candle is fully below EMA (both high and low < EMA)
- **Action**: Sends "Bearish Alert" to Telegram

### Neutral Signal 🟡
- **Condition**: 5-minute candle intersects with EMA
- **Action**: No alert sent

## 🔄 How It Works

1. **Every 5 minutes**, the system:
   - Fetches latest 1-minute candle data for Nifty 50
   - Converts to 5-minute candles using OHLC aggregation
   - Calculates EMA(5) using historical 5-minute data
   - Compares current candle position with EMA
   - Sends alert if signal conditions are met

2. **Token Management**:
   - Uses access token from initial authentication
   - Re-authentication required when token expires (usually daily)

3. **Duplicate Prevention**:
   - Tracks last alert timestamp and signal type
   - Avoids sending duplicate alerts for the same candle

## 📱 Sample Telegram Alerts

### Bullish Alert
```
🟢 BULLISH ALERT - Nifty 50

📅 Time: 2025-08-28 14:30:00
📈 Close: ₹25,245.50
📊 EMA(5): ₹25,190.25

💡 Signal: Candle is fully above EMA
🎯 Trend: Bullish momentum detected

Note: This is an automated alert based on EMA analysis
```

### Status Update
```
🟢 Nifty 50 Status Update

📅 Time: 2025-08-28 15:30:00
💰 Price: ₹24,710.70
📊 EMA(5): ₹24,709.48
📈 Signal: NEUTRAL

Automated monitoring active...
```

## 🔧 Customization

### Change EMA Period
Edit `main.py`:
```python
# Change from EMA 5 to EMA 10
alert_system = NiftyEMAAlerts(ema_period=10, check_interval=300)
```

### Change Check Interval
```python
# Check every 3 minutes instead of 5
alert_system = NiftyEMAAlerts(ema_period=5, check_interval=180)
```

### Add More Indicators
Extend `upstox_client.py` to add RSI, MACD, etc.

## 🧪 Testing

### Test Upstox Connection
```bash
python upstox_client.py
```

### Test Telegram Bot
```bash
python telegram_bot.py
```

## ⚠️ Important Notes

1. **Market Hours**: System works during market hours (9:15 AM - 3:30 PM IST)
2. **Data Source**: Uses 1-minute data from Upstox, converted to 5-minute candles
3. **Token Expiry**: Access tokens expire (usually daily) - re-run `auth.py` when needed
4. **Rate Limits**: Upstox has API rate limits - current interval (5 min) is safe
5. **Network**: Ensure stable internet connection for continuous monitoring
6. **Weekend/Holidays**: No data available when markets are closed

## 📈 Future Enhancements

- [ ] Add support for multiple stocks/indices
- [ ] Implement multiple EMA strategies (EMA crossovers)
- [ ] Add RSI, MACD indicators
- [ ] Web dashboard for monitoring
- [ ] Database storage for historical alerts
- [ ] Backtesting capabilities
- [ ] Position sizing recommendations
- [ ] Auto re-authentication when tokens expire

## 🐛 Troubleshooting

### Common Issues:

1. **"No refresh token available"**
   - This is normal - Upstox doesn't provide refresh tokens
   - Re-run `python auth.py` when token expires

2. **"Failed to fetch data"**
   - Check internet connection
   - Verify Upstox API is working
   - Check if market is open
   - Re-authenticate if token expired

3. **"Telegram message failed"**
   - Verify bot token and chat ID in config.json
   - Ensure bot is added to your chat

4. **"400 Bad Request - Invalid interval"**
   - Fixed in current version - now uses 1minute data
   - Don't manually change intervals to unsupported values

5. **"No data received"**
   - Market might be closed
   - Check if it's a trading day
   - Verify instrument key is correct

### Getting Help:

1. Check error messages in console
2. Verify all credentials in `config.json`
3. Test individual components separately
4. Ensure Python dependencies are installed

## 📜 License

This project is for educational purposes. Use at your own risk. Not financial advice.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Happy Trading! 📈💰**
