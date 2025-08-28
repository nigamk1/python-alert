import os
import json
import requests
from datetime import datetime

def send_telegram_message(message, bot_token, chat_id):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending telegram message: {e}")
        return False

def format_bullish_alert(candle_data):
    """Format bullish signal alert message"""
    time_str = candle_data['datetime'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(candle_data['datetime'], datetime) else str(candle_data['datetime'])
    
    message = f"""
🟢 <b>BULLISH ALERT - Nifty 50</b>

📅 <b>Time:</b> {time_str}
📈 <b>Close:</b> ₹{candle_data['close']:.2f}
📊 <b>EMA({candle_data['ema_period']}):</b> ₹{candle_data['ema']:.2f}

💡 <b>Signal:</b> Candle is fully above EMA
🎯 <b>Trend:</b> Bullish momentum detected

<i>Automated alert from Vercel deployment</i>
    """.strip()
    
    return message
