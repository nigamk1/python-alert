@echo off
REM Nifty 50 EMA Alerts - Netlify Deployment Script for Windows

echo 🚀 Nifty 50 EMA Alerts - Netlify Deployment
echo ============================================

REM Check if Netlify CLI is installed
netlify --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Netlify CLI not found. Installing...
    npm install -g netlify-cli
)

echo ✅ Netlify CLI found

REM Login to Netlify
echo 🔐 Logging into Netlify...
netlify login

REM Deploy the project
echo 🚀 Deploying to Netlify...
netlify deploy --prod

echo.
echo 🎉 Deployment Successful!
echo =========================
echo.
echo 🔧 Next Steps:
echo 1. Configure environment variables in Netlify dashboard
echo 2. Visit your-site.netlify.app/.netlify/functions/auth for authentication
echo 3. Add NETLIFY_FUNCTION_URL to GitHub repository secrets
echo 4. GitHub Actions will automatically trigger alerts every 5 minutes
echo.
echo 📱 You'll receive Telegram alerts for bullish signals!
echo.

echo 🔑 Required Environment Variables (add in Netlify dashboard):
echo =============================================================
echo UPSTOX_CLIENT_ID=your_upstox_client_id
echo UPSTOX_CLIENT_SECRET=your_upstox_client_secret
echo UPSTOX_REDIRECT_URI=https://your-site.netlify.app/.netlify/functions/auth
echo TELEGRAM_BOT_TOKEN=your_telegram_bot_token
echo TELEGRAM_CHAT_ID=your_telegram_chat_id
echo UPSTOX_ACCESS_TOKEN=^<get_from_auth_endpoint^>
echo.
echo 🔗 GitHub Secret (add in repository settings):
echo NETLIFY_FUNCTION_URL=https://your-site.netlify.app/.netlify/functions

pause
