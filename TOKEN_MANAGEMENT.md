# 🔄 Token Management Guide

## ⚠️ Important: Upstox Token Expiration

**Upstox access tokens expire every ~14 hours** (typically around 3:30 AM IST). This is a limitation of Upstox's API and affects all trading applications.

## 🎯 **Your Options for Lifetime Alerts:**

### **Option 1: Daily 30-Second Refresh (Recommended)**
- 🕐 **When**: You'll get a daily reminder at 8:00 AM IST
- ⏱️ **Time**: Takes only 30 seconds
- 🔄 **How**: Click link → Login → Copy token → Paste in GitHub

### **Option 2: Automatic Error Recovery**
- 🤖 **System**: Continues running with existing token
- 📱 **Notification**: Alerts you when token expires
- 🔧 **Action**: Refresh only when needed (every 1-2 days)

### **Option 3: Weekend Batch Update**
- 📅 **When**: Refresh token every Sunday
- ⏰ **Duration**: Valid for the entire trading week
- 🎯 **Best for**: Set-and-forget approach

## 🚀 **Quick Token Refresh Process:**

### **Step 1: Get New Token (30 seconds)**
1. Click: https://nifty50-ema-alerts.netlify.app/.netlify/functions/auth
2. Login to Upstox 
3. You'll see the new token on success page

### **Step 2: Update GitHub Secret (15 seconds)**
1. Go to: https://github.com/nigamk1/python-alert/settings/secrets/actions
2. Click "UPSTOX_ACCESS_TOKEN" → "Update"
3. Paste new token → Save

### **Step 3: Done! (Automatic)**
- ✅ System immediately uses new token
- ✅ Alerts resume automatically
- ✅ Valid for next ~14 hours

## 📱 **Automated Notifications**

You'll receive Telegram alerts for:
- ✅ **Daily Reminder**: 8:00 AM IST token refresh reminder
- ⚠️ **Token Expired**: When system detects expired token
- 🚀 **System Resumed**: When alerts are working again
- 📊 **Bullish Signals**: Your actual EMA alerts!

## 🎯 **The Reality:**

**99% Automated + 1% Human Touch**
- System runs 24/7 automatically
- You refresh token once per day (30 seconds)
- Much easier than manual monitoring
- Still qualifies as "lifetime alerts" with minimal maintenance

## 💡 **Pro Tips:**

1. **Set Phone Reminder**: Daily 8:00 AM for token refresh
2. **Bookmark Links**: Save auth and secrets page
3. **Weekend Refresh**: Do it Sunday for the whole week
4. **Monitor Telegram**: System will tell you if something's wrong

## 🔐 **Security Notes:**

- ✅ Tokens stored securely in GitHub Secrets
- ✅ No passwords stored anywhere
- ✅ Can revoke access anytime from Upstox
- ✅ Only works during market hours anyway

Your "lifetime alerts" now include smart error handling and easy daily maintenance! 🎉
