import time
import json
import os
from datetime import datetime, timedelta
from upstox_client import UpstoxClient
from telegram_bot import send_bullish_alert, send_bearish_alert, send_status_update, send_telegram_alert

class NiftyEMAAlerts:
    def __init__(self, ema_period=5, check_interval=300):
        """
        Initialize Nifty EMA Alert System
        
        Args:
            ema_period: EMA period for calculations (default 5)
            check_interval: Time between checks in seconds (default 300 = 5 minutes)
        """
        self.ema_period = ema_period
        self.check_interval = check_interval
        self.upstox_client = UpstoxClient()
        self.last_alert_timestamp = None
        self.last_signal = None
        self.state_file = "alert_state.json"
        
        # Load previous state
        self.load_state()
        
        print(f"🚀 Nifty 50 EMA Alert System Initialized")
        print(f"   EMA Period: {self.ema_period}")
        print(f"   Check Interval: {self.check_interval} seconds")
    
    def load_state(self):
        """Load previous alert state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.last_alert_timestamp = state.get('last_alert_timestamp')
                    self.last_signal = state.get('last_signal')
                print("📂 Previous state loaded")
        except Exception as e:
            print(f"⚠️ Could not load previous state: {str(e)}")
    
    def save_state(self):
        """Save current alert state to file"""
        try:
            state = {
                'last_alert_timestamp': self.last_alert_timestamp,
                'last_signal': self.last_signal,
                'updated_at': datetime.now().isoformat()
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save state: {str(e)}")
    
    def is_duplicate_alert(self, candle_timestamp, signal_type):
        """
        Check if this alert is a duplicate
        
        Args:
            candle_timestamp: Timestamp of current candle
            signal_type: Type of signal (BULLISH/BEARISH)
        
        Returns:
            bool: True if this is a duplicate alert
        """
        # If no previous alert, this is not a duplicate
        if not self.last_alert_timestamp or not self.last_signal:
            return False
        
        # If signal type changed, this is not a duplicate
        if self.last_signal != signal_type:
            return False
        
        # If same candle timestamp and same signal, it's a duplicate
        if self.last_alert_timestamp == candle_timestamp:
            return True
        
        return False
    
    def should_send_alert(self, candle_data, signal_type):
        """
        Determine if an alert should be sent
        
        Args:
            candle_data: Current candle data
            signal_type: Signal type (BULLISH/BEARISH/NEUTRAL)
        
        Returns:
            bool: True if alert should be sent
        """
        # Only send alerts for BULLISH signals
        if signal_type != 'BULLISH':
            return False
        
        # Check for duplicate alerts
        if self.is_duplicate_alert(candle_data['timestamp'], signal_type):
            return False
        
        return True
    
    def send_alert(self, candle_data, signal_type):
        """
        Send appropriate alert based on signal type
        
        Args:
            candle_data: Current candle data
            signal_type: Signal type
        
        Returns:
            bool: True if alert sent successfully
        """
        try:
            if signal_type == 'BULLISH':
                success = send_bullish_alert(candle_data)
            else:
                return False  # Only send bullish alerts
            
            if success:
                # Update alert state
                self.last_alert_timestamp = candle_data['timestamp']
                self.last_signal = signal_type
                self.save_state()
                
                print(f"✅ {signal_type} alert sent successfully")
            else:
                print(f"❌ Failed to send {signal_type} alert")
            
            return success
            
        except Exception as e:
            print(f"❌ Error sending alert: {str(e)}")
            return False
    
    def check_and_alert(self):
        """
        Check current market condition and send alerts if needed
        
        Returns:
            dict: Status information about the check
        """
        try:
            print(f"\n🔍 Checking Nifty 50 at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get latest candle data with EMA
            candle_data = self.upstox_client.get_nifty50_with_ema(self.ema_period)
            
            # Determine signal type
            signal_type = self.upstox_client.get_signal_type(candle_data)
            
            # Print current status
            print(f"   Price: ₹{candle_data['close']:.2f}")
            print(f"   EMA({self.ema_period}): ₹{candle_data['ema']:.2f}")
            print(f"   Signal: {signal_type}")
            
            # Check if alert should be sent
            if self.should_send_alert(candle_data, signal_type):
                self.send_alert(candle_data, signal_type)
                alert_sent = True
            else:
                if signal_type == 'BULLISH':
                    print(f"   ⏭️ Duplicate {signal_type} alert skipped")
                elif signal_type == 'BEARISH':
                    print(f"   📉 Bearish signal detected but not alerting (bullish only mode)")
                else:
                    print(f"   ⏸️ No alert conditions met")
                alert_sent = False
            
            return {
                'success': True,
                'timestamp': datetime.now(),
                'candle_data': candle_data,
                'signal_type': signal_type,
                'alert_sent': alert_sent
            }
            
        except Exception as e:
            error_msg = f"❌ Error during check: {str(e)}"
            print(error_msg)
            
            # Send error notification
            send_telegram_alert(f"🚨 <b>Nifty EMA Alert Error</b>\n\n{error_msg}")
            
            return {
                'success': False,
                'timestamp': datetime.now(),
                'error': str(e),
                'alert_sent': False
            }
    
    def run_continuous(self):
        """
        Run continuous monitoring loop
        """
        print(f"\n🎯 Starting continuous monitoring...")
        print(f"   Checking every {self.check_interval} seconds")
        print(f"   Press Ctrl+C to stop\n")
        
        # Send startup notification
        startup_msg = f"""
🤖 <b>Nifty 50 EMA Alert Bot Started</b>

⚙️ <b>Configuration:</b>
   • EMA Period: {self.ema_period}
   • Check Interval: {self.check_interval} seconds
   • Target: NSE Nifty 50
   • Alert Mode: BULLISH ONLY 🟢

📊 <b>Alert Conditions:</b>
   • 🟢 Bullish: Candle fully above EMA (ALERTS ENABLED)
   • 🔴 Bearish: Candle fully below EMA (monitoring only)

🚀 Monitoring started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        send_telegram_alert(startup_msg)
        
        check_count = 0
        
        try:
            while True:
                check_count += 1
                
                # Perform check
                result = self.check_and_alert()
                
                # Send periodic status updates (every 12 checks = 1 hour if checking every 5 minutes)
                if check_count % 12 == 0 and result['success']:
                    send_status_update(result['candle_data'], result['signal_type'])
                
                # Wait for next check
                print(f"   💤 Waiting {self.check_interval} seconds for next check...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Monitoring stopped by user")
            
            # Send shutdown notification
            shutdown_msg = f"""
🛑 <b>Nifty 50 EMA Alert Bot Stopped</b>

📊 <b>Session Summary:</b>
   • Total Checks: {check_count}
   • Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 Bot can be restarted anytime by running main.py
            """.strip()
            
            send_telegram_alert(shutdown_msg)
        
        except Exception as e:
            error_msg = f"🚨 Critical error in monitoring loop: {str(e)}"
            print(f"\n❌ {error_msg}")
            send_telegram_alert(f"🚨 <b>Critical Alert Bot Error</b>\n\n{error_msg}")

def main():
    """Main function to start the EMA alert system"""
    print("=" * 60)
    print("🚀 NIFTY 50 EMA ALERT SYSTEM")
    print("=" * 60)
    
    try:
        # Initialize alert system
        alert_system = NiftyEMAAlerts(ema_period=5, check_interval=300)
        
        # Run continuous monitoring
        alert_system.run_continuous()
        
    except Exception as e:
        print(f"❌ Failed to start alert system: {str(e)}")
        print("\n🔧 Please check:")
        print("   1. Run auth.py first to setup authentication")
        print("   2. Update config.json with your API keys")
        print("   3. Ensure internet connection is working")

if __name__ == "__main__":
    main()
