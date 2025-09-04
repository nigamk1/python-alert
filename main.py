import asyncio
import websockets
import requests
import pandas as pd
import time
import json
from datetime import datetime, timedelta, date
from telegram import Bot

# --- CONFIGURATION ---
UPSTOX_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4QkFDOUwiLCJqdGkiOiI2OGI5MzNlNjE2OWU2MjE3MGFjMTY0OTgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6dHJ1ZSwiaWF0IjoxNzU2OTY3OTEwLCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3NTcwMjMyMDB9.3hx1oyaFY7K0888967rCjkD6iq21r8i-uqK5Bcln94c"
TELEGRAM_BOT_TOKEN = "7081191913:AAFtW8vR6AXsavzKw7RmuYgiSTFLcOhb7gg"
TELEGRAM_CHAT_ID = "801765025"
INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"
INTERVAL = "5minute"

# --- EMA CALCULATOR ---
class EMACalculator:
    def __init__(self, period):
        self.period = period
        self.multiplier = 2 / (period + 1)
        self.ema = None
        self.prices = []

    def add_price(self, price):
        self.prices.append(price)
        if len(self.prices) < self.period:
            print(f"🔄 EMA data collection: {len(self.prices)}/{self.period} candles")
            return None
        if self.ema is None:
            self.ema = sum(self.prices[-self.period:]) / self.period
            print(f"📊 Initial EMA calculated using SMA of {self.period} prices: {self.ema:.2f}")
        else:
            old_ema = self.ema
            self.ema = (price * self.multiplier) + (self.ema * (1 - self.multiplier))
            print(f"📊 EMA updated: {old_ema:.2f} → {self.ema:.2f} (price: {price})")
        return self.ema
   
    def get_current_ema(self):
        """Get the current EMA value"""
        return self.ema

# --- FETCH HISTORICAL (latest available trading day) ---
def fetch_historical_data():
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
    }

    check_date = date.today()
    while True:
        day_str = check_date.strftime("%Y-%m-%d")
        url = f"https://api.upstox.com/v3/historical-candle/{INSTRUMENT_KEY}/day/1/{day_str}/{day_str}"
        resp = requests.get(url, headers=headers)

        if resp.status_code == 200:
            candles = resp.json().get("data", {}).get("candles", [])
            if candles:
                df = pd.DataFrame(candles, columns=["datetime", "open", "high", "low", "close", "volume"])
                df["datetime"] = pd.to_datetime(df["datetime"])
                return df
        check_date -= timedelta(days=1)

# --- FETCH LATEST INTRADAY 1-MINUTE DATA AND CREATE 5-MINUTE CANDLES ---
def fetch_intraday_data():
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
    }
   
    # Try current day first, then go back to find the last trading day
    check_date = date.today()
    max_attempts = 7  # Check up to 7 days back
   
    for attempt in range(max_attempts):
        date_str = check_date.strftime("%Y-%m-%d")
        url = f"https://api.upstox.com/v2/historical-candle/{INSTRUMENT_KEY}/1minute/{date_str}/{date_str}"
        print(f"🔗 API URL: {url}")
        resp = requests.get(url, headers=headers)
        print(f"📡 Response Status: {resp.status_code}")
       
        if resp.status_code == 200:
            data = resp.json()
            candles = data.get("data", {}).get("candles", [])
            if candles:
                # Check the actual structure of the data
                print(f"📊 Sample candle data: {candles[0] if candles else 'No candles'}")
                print(f"📊 Number of columns in data: {len(candles[0]) if candles else 0}")
               
                # Create DataFrame with all available columns first
                df = pd.DataFrame(candles)
                print(f"📊 DataFrame columns: {df.columns.tolist()}")
               
                # Rename columns based on typical Upstox API structure
                if len(df.columns) == 7:
                    df.columns = ["datetime", "open", "high", "low", "close", "volume", "oi"]
                elif len(df.columns) == 6:
                    df.columns = ["datetime", "open", "high", "low", "close", "volume"]
                else:
                    print(f"❌ Unexpected number of columns: {len(df.columns)}")
                    return None
               
                df["datetime"] = pd.to_datetime(df["datetime"])
                print(f"✅ Received {len(df)} 1-minute candles for {date_str}")
               
                # Convert 1-minute candles to 5-minute candles
                df_5min = convert_to_5min_candles(df)
                if not df_5min.empty:
                    print(f"✅ Created {len(df_5min)} 5-minute candles")
                    return df_5min
                else:
                    print("❌ No 5-minute candles created")
            else:
                print(f"❌ No candles available for {date_str}")
        else:
            print(f"❌ API Error: {resp.text}")
       
        # Move to previous day
        check_date -= timedelta(days=1)
   
    print(f"❌ No trading data found in the last {max_attempts} days")
    return None

# --- CONVERT 1-MINUTE TO 5-MINUTE CANDLES ---
def convert_to_5min_candles(df_1min):
    if df_1min.empty:
        return pd.DataFrame()
   
    # Set datetime as index for resampling
    df_1min.set_index('datetime', inplace=True)
   
    # Define aggregation rules
    agg_rules = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
   
    # Add 'oi' if it exists
    if 'oi' in df_1min.columns:
        agg_rules['oi'] = 'last'
   
    # Resample to 5-minute intervals
    df_5min = df_1min.resample('5T').agg(agg_rules).dropna()
   
    # Reset index to get datetime as column again
    df_5min.reset_index(inplace=True)
   
    return df_5min

# --- REAL-TIME CANDLE GENERATOR ---
class RealTimeCandleGenerator:
    def __init__(self, interval_minutes=5):
        self.interval_minutes = interval_minutes
        self.current_candle = None
        self.completed_candles = []
        self.ema_calculator = EMACalculator(5)

    def add_tick(self, price, timestamp):
        """Add a tick and return completed candles if any"""
        tick_time = datetime.fromtimestamp(timestamp / 1000)
       
        # Check if we need to start a new candle
        if self.current_candle is None:
            # Calculate candle start time (aligned to interval) for first candle
            minutes = (tick_time.minute // self.interval_minutes) * self.interval_minutes
            candle_start = tick_time.replace(minute=minutes, second=0, microsecond=0)
            candle_end = candle_start + timedelta(minutes=self.interval_minutes)
           
            # Start new candle
            self.current_candle = {
                'start_time': candle_start,
                'end_time': candle_end,
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'tick_count': 1,
                'last_update': tick_time
            }
        elif tick_time >= self.current_candle['end_time']:
            # Complete the previous candle
            self.completed_candles.append(self.current_candle)
           
            # Calculate new candle start time (aligned to interval)
            minutes = (tick_time.minute // self.interval_minutes) * self.interval_minutes
            candle_start = tick_time.replace(minute=minutes, second=0, microsecond=0)
            candle_end = candle_start + timedelta(minutes=self.interval_minutes)
               
            # Start new candle
            self.current_candle = {
                'start_time': candle_start,
                'end_time': candle_end,
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'tick_count': 1,
                'last_update': tick_time
            }
        else:
            # Update current candle
            self.current_candle['high'] = max(self.current_candle['high'], price)
            self.current_candle['low'] = min(self.current_candle['low'], price)
            self.current_candle['close'] = price
            self.current_candle['tick_count'] += 1
            self.current_candle['last_update'] = tick_time
       
        # Return completed candles
        if self.completed_candles:
            completed = self.completed_candles[:]
            self.completed_candles = []
            return completed
        return []

    def get_current_candle(self):
        return self.current_candle

# --- REAL-TIME WEBSOCKET FEED ---
async def real_time_nifty_monitor():
    """Connect to Upstox WebSocket and monitor real-time Nifty 50 data"""
   
    candle_generator = RealTimeCandleGenerator(5)  # 5-minute candles
    ema_calculator = EMACalculator(5)  # 5-period EMA
   
    # Test Telegram first
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        test_msg = "🔔 Real-Time Nifty 50 EMA Monitor Started!"
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=test_msg)
        print("✅ Telegram test message sent!")
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return

    # Pre-populate EMA with recent historical 5-minute candles
    print("📊 Fetching recent historical data to initialize EMA...")
    try:
        historical_df = fetch_intraday_data()
        if historical_df is not None and not historical_df.empty:
            recent_candles = historical_df.tail(10)  # Get last 10 candles
            for _, candle in recent_candles.iterrows():
                ema_calculator.add_price(candle['close'])
            print(f"✅ EMA initialized with {len(recent_candles)} historical candles")
        else:
            print("⚠️  No historical data available, will build EMA from live data")
    except Exception as e:
        print(f"⚠️  Error fetching historical data: {e}, will build EMA from live data")

    # For now, simulate real-time data using API polling (since WebSocket has header issues)
    print("📡 Starting real-time simulation using API polling...")
   
    last_price = None
   
    while True:
        try:
            # Get current market price (simulate real-time)
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
            }
           
            # Use quote API for current price
            url = f"https://api.upstox.com/v2/market-quote/quotes?instrument_key={INSTRUMENT_KEY}"
            print(f"🔗 Fetching data from: {url}")
            response = requests.get(url, headers=headers)
            print(f"📡 Response Status: {response.status_code}")
           
            if response.status_code == 200:
                data = response.json()
                print(f"📊 API Response: {data}")
               
                if 'data' in data:
                    # Check for both possible key formats
                    quote_data = None
                    for key in data['data']:
                        if 'Nifty 50' in key:
                            quote_data = data['data'][key]
                            print(f"📊 Found Quote Data with key '{key}': {quote_data}")
                            break
                   
                    if quote_data:
                        current_price = quote_data.get('last_price', quote_data.get('ltp', 0))
                       
                        if current_price and current_price != last_price:
                            last_price = current_price
                            timestamp = int(time.time() * 1000)
                           
                            print(f"🔴 LIVE: {datetime.now().strftime('%H:%M:%S')} | Nifty 50: ₹{current_price}")
                           
                            # Show current EMA value for comparison
                            current_ema = ema_calculator.get_current_ema()
                            if current_ema:
                                ema_diff = current_price - current_ema
                                ema_diff_pct = (ema_diff / current_ema) * 100
                                print(f"📈 Current 5-EMA: ₹{current_ema:.2f} | Diff: {ema_diff:+.2f} ({ema_diff_pct:+.2f}%)")
                           
                            # Add tick to candle generator
                            completed_candles = candle_generator.add_tick(current_price, timestamp)
                           
                            # Process completed candles
                            for candle in completed_candles:
                                ema = ema_calculator.add_price(candle['close'])
                               
                                print(f"\n🎯 NEW 5-MIN CANDLE COMPLETED:")
                                print(f"⏰ Time: {candle['start_time'].strftime('%H:%M:%S')} - {candle['end_time'].strftime('%H:%M:%S')}")
                                print(f"💰 OHLC: Open={candle['open']:.2f} | High={candle['high']:.2f} | Low={candle['low']:.2f} | Close={candle['close']:.2f}")
                               
                                if ema is not None:
                                    print(f"📈 5-EMA: ₹{ema:.2f}")
                                    print(f"🔍 Analysis:")
                                    print(f"   • Low ({candle['low']:.2f}) > EMA ({ema:.2f}) = {candle['low'] > ema}")
                                    print(f"   • High ({candle['high']:.2f}) > EMA ({ema:.2f}) = {candle['high'] > ema}")
                                    print(f"   • Open ({candle['open']:.2f}) > EMA ({ema:.2f}) = {candle['open'] > ema}")
                                    print(f"   • Close ({candle['close']:.2f}) > EMA ({ema:.2f}) = {candle['close'] > ema}")
                                   
                                    # Check alert condition: ENTIRE candle completely above EMA
                                    candle_above_ema = (candle['low'] > ema and 
                                                       candle['high'] > ema and
                                                       candle['open'] > ema and 
                                                       candle['close'] > ema)
                                   
                                    print(f"🎯 ALERT CHECK: Entire candle above EMA = {candle_above_ema}")
                                   
                                    if candle_above_ema:
                                        print(f"🚀 ALERT CONDITION MET!")
                                       
                                        # Send alert for current candle
                                        alert_msg = (
                                            f"🚀 NIFTY 50 EMA BREAKOUT ALERT!\n\n"
                                            f"🕐 Time: {candle['end_time'].strftime('%d-%m-%Y %H:%M:%S')}\n"
                                            f"💰 OHLC: {candle['open']:.2f} | {candle['high']:.2f} | {candle['low']:.2f} | {candle['close']:.2f}\n"
                                            f"📈 5-EMA: ₹{ema:.2f}\n\n"
                                            f"✅ ENTIRE Candle ABOVE 5-EMA\n"
                                            f"📈 Min Distance: +₹{candle['low'] - ema:.2f} ({((candle['low'] - ema) / ema) * 100:.2f}%)\n"
                                            f"📊 Max Distance: +₹{candle['high'] - ema:.2f} ({((candle['high'] - ema) / ema) * 100:.2f}%)"
                                        )
                                        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=alert_msg)
                                        print(f"✅ Telegram alert sent!")
                                    else:
                                        print(f"❌ ALERT CONDITION FAILED:")
                                        if candle['low'] <= ema:
                                            print(f"   ❌ Low {candle['low']:.2f} <= EMA {ema:.2f}")
                                        if candle['high'] <= ema:
                                            print(f"   ❌ High {candle['high']:.2f} <= EMA {ema:.2f}")
                                        if candle['open'] <= ema:
                                            print(f"   ❌ Open {candle['open']:.2f} <= EMA {ema:.2f}")
                                        if candle['close'] <= ema:
                                            print(f"   ❌ Close {candle['close']:.2f} <= EMA {ema:.2f}")
                                else:
                                    print(f"⏳ EMA not ready yet (need 5 candles). Current count: {len(ema_calculator.prices)}")
                           
                            # Show current candle progress with corrected time calculation
                            current = candle_generator.get_current_candle()
                            if current:
                                now = datetime.now()
                                if current['end_time'] > now:
                                    remaining_time = current['end_time'] - now
                                    remaining_seconds = int(remaining_time.total_seconds())
                                    remaining_minutes = remaining_seconds // 60
                                    remaining_secs = remaining_seconds % 60
                                    time_str = f"{remaining_minutes}:{remaining_secs:02d}"
                                else:
                                    time_str = "00:00"
                                print(f"📊 Current 5-min candle: O={current['open']:.2f} | H={current['high']:.2f} | L={current['low']:.2f} | C={current['close']:.2f} | Ends in: {time_str}")
                        else:
                            print(f"⏸️  No price change. Current: {current_price}, Last: {last_price}")
                    else:
                        print("❌ No Nifty 50 data found in response")
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
           
            print(f"⏰ Waiting 5 seconds before next check...")
            await asyncio.sleep(5)  # Check every 5 seconds
           
        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(10)

# --- MAIN FUNCTION ---
async def main():
    print("🚀 Starting REAL-TIME Nifty 50 EMA Alert Bot...")
    await real_time_nifty_monitor()

if __name__ == "__main__":
    asyncio.run(main())
