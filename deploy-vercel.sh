#!/bin/bash

# Nifty 50 EMA Alerts - Vercel Deployment Script
# This script automates the deployment process

echo "🚀 Nifty 50 EMA Alerts - Vercel Deployment"
echo "==========================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "✅ Vercel CLI found"

# Login to Vercel
echo "🔐 Logging into Vercel..."
vercel login

# Deploy the project
echo "🚀 Deploying to Vercel..."
vercel --prod

# Get the deployment URL
DEPLOYMENT_URL=$(vercel --prod --confirm 2>&1 | grep -o 'https://[^[:space:]]*')

echo ""
echo "🎉 Deployment Successful!"
echo "========================="
echo ""
echo "📍 Your app is live at: $DEPLOYMENT_URL"
echo ""
echo "🔧 Next Steps:"
echo "1. Set up environment variables in Vercel dashboard"
echo "2. Visit $DEPLOYMENT_URL/api/auth for one-time authentication"
echo "3. Add the access token to environment variables"
echo "4. Your system will automatically start monitoring!"
echo ""
echo "📱 You'll receive Telegram alerts for bullish signals every 5 minutes"
echo ""

# Show environment variables template
echo "🔑 Required Environment Variables:"
echo "=================================="
echo "UPSTOX_CLIENT_ID=your_upstox_client_id"
echo "UPSTOX_CLIENT_SECRET=your_upstox_client_secret" 
echo "UPSTOX_REDIRECT_URI=$DEPLOYMENT_URL/api/auth"
echo "TELEGRAM_BOT_TOKEN=your_telegram_bot_token"
echo "TELEGRAM_CHAT_ID=your_telegram_chat_id"
echo "UPSTOX_ACCESS_TOKEN=<get_from_auth_endpoint>"
echo ""
echo "💡 Add these in your Vercel dashboard under Settings > Environment Variables"
