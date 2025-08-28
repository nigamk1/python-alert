import os
import json
from datetime import datetime
from upstox_utils import UpstoxVercelClient
from telegram_utils import send_telegram_message, format_bullish_alert

# Vercel KV or simple state management
class StateManager:
    def __init__(self):
        self.state_key = "last_alert_state"
    
    def get_last_alert_state(self):
        """Get last alert state from environment or return default"""
        # In production, this could use Vercel KV, Redis, or a database
        # For now, we'll use a simple approach with environment variables
        return {
            'last_alert_timestamp': None,
            'last_signal': None
        }
    
    def save_alert_state(self, timestamp, signal):
        """Save alert state (in production, save to persistent storage)"""
        # In a real deployment, you'd save this to Vercel KV or a database
        print(f"Alert state saved: {timestamp}, {signal}")

def handler(request):
    """Main handler for Vercel serverless function"""
    try:
        # Get environment variables
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing Telegram credentials'})
            }
        
        # Initialize clients
        upstox_client = UpstoxVercelClient()
        state_manager = StateManager()
        
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
            # Get last alert state
            last_state = state_manager.get_last_alert_state()
            
            # Check if we should send alert (avoid duplicates)
            should_alert = (
                last_state['last_alert_timestamp'] != candle_data['timestamp'] or
                last_state['last_signal'] != 'BULLISH'
            )
            
            if should_alert:
                message = format_bullish_alert(candle_data)
                alert_sent = send_telegram_message(message, bot_token, chat_id)
                
                if alert_sent:
                    state_manager.save_alert_state(candle_data['timestamp'], 'BULLISH')
                    response_data['alert_sent'] = True
                    response_data['message'] = 'Bullish alert sent successfully'
                else:
                    response_data['message'] = 'Failed to send alert'
            else:
                response_data['message'] = 'Duplicate alert skipped'
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
