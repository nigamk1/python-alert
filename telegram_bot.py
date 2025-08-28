import json
import requests
from datetime import datetime

class TelegramBot:
    def __init__(self, config_path="config.json"):
        """Initialize Telegram bot with config"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.bot_token = config['telegram']['bot_token']
        self.chat_id = config['telegram']['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message, parse_mode='HTML'):
        """
        Send message to Telegram chat
        
        Args:
            message: Message text to send
            parse_mode: Message format ('HTML', 'Markdown', or None)
        
        Returns:
            bool: True if message sent successfully
        """
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                return True
            else:
                print(f"❌ Telegram API error: {result.get('description', 'Unknown error')}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send Telegram message: {str(e)}")
            return False
    
    def test_connection(self):
        """Test Telegram bot connection"""
        test_message = "🧪 Nifty 50 EMA Alert Bot - Connection Test"
        return self.send_message(test_message)

def send_telegram_alert(message):
    """
    Helper function to send Telegram alert
    
    Args:
        message: Alert message to send
    
    Returns:
        bool: True if alert sent successfully
    """
    try:
        bot = TelegramBot()
        return bot.send_message(message)
    except Exception as e:
        print(f"❌ Failed to send alert: {str(e)}")
        return False

def format_bullish_alert(candle_data):
    """Format bullish signal alert message"""
    time_str = candle_data['datetime'].strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"""
🟢 <b>BULLISH ALERT - Nifty 50</b>

📅 <b>Time:</b> {time_str}
📈 <b>Close:</b> ₹{candle_data['close']:.2f}
📊 <b>EMA({candle_data['ema_period']}):</b> ₹{candle_data['ema']:.2f}

💡 <b>Signal:</b> Candle is fully above EMA
🎯 <b>Trend:</b> Bullish momentum detected

<i>Note: This is an automated alert based on EMA analysis</i>
    """.strip()
    
    return message

def format_bearish_alert(candle_data):
    """Format bearish signal alert message"""
    time_str = candle_data['datetime'].strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"""
🔴 <b>BEARISH ALERT - Nifty 50</b>

📅 <b>Time:</b> {time_str}
📉 <b>Close:</b> ₹{candle_data['close']:.2f}
📊 <b>EMA({candle_data['ema_period']}):</b> ₹{candle_data['ema']:.2f}

💡 <b>Signal:</b> Candle is fully below EMA
🎯 <b>Trend:</b> Bearish momentum detected

<i>Note: This is an automated alert based on EMA analysis</i>
    """.strip()
    
    return message

def format_status_update(candle_data, signal_type):
    """Format general status update message"""
    time_str = candle_data['datetime'].strftime('%Y-%m-%d %H:%M:%S')
    
    signal_emoji = {
        'BULLISH': '🟢',
        'BEARISH': '🔴',
        'NEUTRAL': '🟡'
    }
    
    message = f"""
{signal_emoji.get(signal_type, '⚪')} <b>Nifty 50 Status Update</b>

📅 <b>Time:</b> {time_str}
💰 <b>Price:</b> ₹{candle_data['close']:.2f}
📊 <b>EMA({candle_data['ema_period']}):</b> ₹{candle_data['ema']:.2f}
📈 <b>Signal:</b> {signal_type}

<i>Automated monitoring active...</i>
    """.strip()
    
    return message

def send_bullish_alert(candle_data):
    """Send bullish alert to Telegram"""
    message = format_bullish_alert(candle_data)
    return send_telegram_alert(message)

def send_bearish_alert(candle_data):
    """Send bearish alert to Telegram"""
    message = format_bearish_alert(candle_data)
    return send_telegram_alert(message)

def send_status_update(candle_data, signal_type):
    """Send status update to Telegram"""
    message = format_status_update(candle_data, signal_type)
    return send_telegram_alert(message)

def test_telegram():
    """Test Telegram bot functionality"""
    try:
        print("🧪 Testing Telegram Bot...")
        
        bot = TelegramBot()
        
        if bot.test_connection():
            print("✅ Telegram bot connection successful!")
            return True
        else:
            print("❌ Telegram bot connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Telegram test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_telegram()
