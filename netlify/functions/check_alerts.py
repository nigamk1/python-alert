import json
import os
import sys
import urllib.parse
from datetime import datetime, timedelta

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import requests
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Import error: {e}")

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

<i>Automated alert from Netlify deployment</i>
    """.strip()
    
    return message

class UpstoxNetlifyClient:
    def __init__(self):
        self.base_url = "https://api.upstox.com/v2"
        self.access_token = os.environ.get('UPSTOX_ACCESS_TOKEN')
        
        if not self.access_token:
            raise Exception("UPSTOX_ACCESS_TOKEN environment variable not set")
        
        self.headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
    
    def get_historical_data(self, instrument_key, interval="1minute", days_back=3):
        """Get historical candle data"""
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        encoded_instrument = urllib.parse.quote(instrument_key, safe='')
        url = f"{self.base_url}/historical-candle/{encoded_instrument}/{interval}/{to_date.strftime('%Y-%m-%d')}/{from_date.strftime('%Y-%m-%d')}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        if data['status'] != 'success':
            raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
        
        candles = data['data']['candles']
        if not candles:
            raise Exception("No candle data received")
            
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('datetime').reset_index(drop=True)
        
        return df
    
    def resample_to_5min(self, df):
        """Convert 1-minute data to 5-minute candles"""
        df_copy = df.copy()
        df_copy.set_index('datetime', inplace=True)
        
        resampled = df_copy.resample('5T').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        resampled.reset_index(inplace=True)
        resampled['timestamp'] = resampled['datetime']
        
        return resampled
    
    def calculate_ema(self, prices, period=5):
        """Calculate EMA"""
        prices = pd.Series(prices)
        return prices.ewm(span=period, adjust=False).mean()
    
    def get_nifty50_with_ema(self, ema_period=5):
        """Get Nifty 50 data with EMA"""
        possible_instruments = [
            "NSE_INDEX|Nifty 50",
            "NSE_INDEX|NIFTY 50",
            "NSE_INDEX|Nifty50",
            "NSE_INDEX|NIFTY50"
        ]
        
        for instrument in possible_instruments:
            try:
                df_1min = self.get_historical_data(instrument, interval="1minute", days_back=3)
                df = self.resample_to_5min(df_1min)
                
                df['ema'] = self.calculate_ema(df['close'], ema_period)
                latest = df.iloc[-1]
                
                return {
                    'timestamp': latest['timestamp'],
                    'datetime': latest['datetime'],
                    'open': float(latest['open']),
                    'high': float(latest['high']),
                    'low': float(latest['low']),
                    'close': float(latest['close']),
                    'volume': int(latest['volume']) if pd.notna(latest['volume']) else 0,
                    'ema': float(latest['ema']),
                    'ema_period': ema_period,
                    'instrument': instrument
                }
            except Exception:
                continue
        
        raise Exception("Failed to get data from any Nifty 50 instrument")
    
    def is_bullish_signal(self, candle_data):
        """Check if bullish signal"""
        return candle_data['low'] > candle_data['ema']

def handler(event, context):
    """Netlify function handler"""
    try:
        # Get environment variables
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing Telegram credentials'})
            }
        
        # Initialize client
        upstox_client = UpstoxNetlifyClient()
        
        # Get current market data
        candle_data = upstox_client.get_nifty50_with_ema(ema_period=5)
        
        # Check for bullish signal
        is_bullish = upstox_client.is_bullish_signal(candle_data)
        
        response_data = {
            'timestamp': datetime.now().isoformat(),
            'price': candle_data['close'],
            'ema': candle_data['ema'],
            'signal': 'BULLISH' if is_bullish else 'NEUTRAL',
            'alert_sent': False
        }
        
        # Send alert if bullish signal detected
        if is_bullish:
            message = format_bullish_alert(candle_data)
            alert_sent = send_telegram_message(message, bot_token, chat_id)
            
            if alert_sent:
                response_data['alert_sent'] = True
                response_data['message'] = 'Bullish alert sent successfully'
            else:
                response_data['message'] = 'Failed to send alert'
        else:
            response_data['message'] = 'No alert conditions met'
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        error_message = f"Error in alert check: {str(e)}"
        
        # Send error notification
        try:
            bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            chat_id = os.environ.get('TELEGRAM_CHAT_ID')
            if bot_token and chat_id:
                error_alert = f"🚨 <b>Nifty EMA Alert Error</b>\n\n{error_message}"
                send_telegram_message(error_alert, bot_token, chat_id)
        except:
            pass
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': error_message})
        }
