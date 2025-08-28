# 📅 Daily Routine for Your Nifty 50 EMA Alerts

## 🌅 **MORNING ROUTINE (30 seconds - once per day)**

### **⏰ When You Wake Up (8:00 AM - 9:00 AM):**

**📱 Check Your Telegram:**
- Look for daily reminder message (arrives at 8:00 AM IST)
- Check if there were any overnight errors

**🔄 Refresh Token (30 seconds):**
1. **Click this link**: https://nifty50-ema-alerts.netlify.app/.netlify/functions/auth
2. **Login to Upstox** (use your usual credentials)  
3. **Copy the new token** from the success page
4. **Update GitHub Secret**: https://github.com/nigamk1/python-alert/settings/secrets/actions
   - Click "UPSTOX_ACCESS_TOKEN" 
   - Click "Update"
   - Paste new token
   - Click "Update secret"

**✅ Done! Your system is ready for the day!**

---

## 🏢 **DURING MARKET HOURS (9:15 AM - 3:30 PM)**

### **What Happens Automatically:**
- ✅ System checks Nifty 50 every 5 minutes
- ✅ Calculates EMA(5) in real-time  
- ✅ Sends bullish signals to your Telegram
- ✅ Handles all monitoring automatically

### **What You Do:**
- 📱 **Just check Telegram** for bullish alerts!
- 🎯 **No manual monitoring needed**
- ☕ **Continue your normal day**

---

## 🌙 **EVENING (Optional Check)**

### **📊 Quick Status Check:**
- Visit: https://github.com/nigamk1/python-alert/actions
- See how many signals were checked today
- Verify system ran without errors

---

## 🎯 **WHAT TO EXPECT:**

### **📱 Telegram Messages You'll Receive:**

**🌅 Daily (8:00 AM):**
```
🔄 DAILY TOKEN REFRESH REMINDER
📅 Date: 2025-08-29
⚠️ Action Required: Refresh token for today's monitoring
```

**🚀 During Market (when bullish):**
```
🚀 BULLISH EMA SIGNAL
📊 Nifty 50: ₹24,850.50
📈 EMA(5): ₹24,820.25
🔥 Signal: BULLISH
⏰ Time: 2025-08-29 10:30:00
```

**⚠️ If Issues (rare):**
```
⚠️ ALERT SYSTEM ERROR
❌ Error: Token expired
System will retry in 5 minutes.
```

---

## 🏃‍♂️ **QUICK REFERENCE:**

| **Task** | **When** | **Time** | **Link** |
|----------|----------|----------|----------|
| Refresh Token | Daily 8-9 AM | 30 sec | [🔐 Auth](https://nifty50-ema-alerts.netlify.app/.netlify/functions/auth) |
| Update Secret | After token refresh | 15 sec | [⚙️ Secrets](https://github.com/nigamk1/python-alert/settings/secrets/actions) |
| Check Status | Optional evening | 10 sec | [📊 Actions](https://github.com/nigamk1/python-alert/actions) |

---

## 💡 **PRO TIPS:**

1. **📱 Bookmark links** on your phone for quick access
2. **⏰ Set phone alarm** for 8:30 AM as backup reminder
3. **📋 Save credentials** in password manager for faster login
4. **🔄 Weekend refresh** can cover Monday-Tuesday if done Sunday night

---

## 🎉 **THAT'S IT!**

**Your "lifetime alerts" = 30 seconds daily maintenance + automated 24/7 monitoring!**

Much easier than manual chart watching! 📈✨
