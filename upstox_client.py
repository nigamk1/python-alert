import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from auth import get_access_token

class UpstoxClient:
    def __init__(self):
        """Initialize Upstox client with authentication"""
        self.base_url = "https://api.upstox.com/v2"
        self.access_token = None
        self.headers = None
        self._authenticate()
    
    def _authenticate(self):
        """Get access token and set up headers"""
        self.access_token = get_access_token()
        if not self.access_token:
            raise Exception("Failed to get access token. Please run auth.py first.")
        
        self.headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
    
    def _refresh_token_if_needed(self):
        """Refresh token if current one is expired"""
        try:
            # Test current token with a simple API call
            response = requests.get(
                f"{self.base_url}/user/profile", 
                headers=self.headers
            )
            
            if response.status_code == 401:  # Unauthorized - token expired
                print("🔄 Access token expired, refreshing...")
                self._authenticate()
            elif response.status_code != 200:
                print(f"⚠️ API response: {response.status_code} - {response.text}")
                self._authenticate()
                
        except Exception as e:
            print(f"⚠️ Token validation failed: {str(e)}")
            # Don't re-authenticate immediately, let the calling function handle the error
    
    def get_historical_data(self, instrument_key, interval="1minute", days_back=10):
        """
        Get historical candle data for an instrument
        
        Args:
            instrument_key: Instrument identifier (e.g., "NSE_INDEX|Nifty 50")
            interval: Candle interval (1minute, 30minute, day, week, month)
            days_back: Number of days to fetch data
        """
        self._refresh_token_if_needed()
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        # Properly encode the instrument key for URL
        import urllib.parse
        encoded_instrument = urllib.parse.quote(instrument_key, safe='')
        
        url = f"{self.base_url}/historical-candle/{encoded_instrument}/{interval}/{to_date.strftime('%Y-%m-%d')}/{from_date.strftime('%Y-%m-%d')}"
        
        try:
            print(f"🔗 Fetching data from: {url}")
            response = requests.get(url, headers=self.headers)
            
            # Print response for debugging
            print(f"📊 Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Response text: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'success':
                raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
            
            # Convert to DataFrame
            candles = data['data']['candles']
            if not candles:
                raise Exception("No candle data received")
                
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
            
            # Convert timestamp to datetime
            df['datetime'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('datetime').reset_index(drop=True)
            
            print(f"✅ Retrieved {len(df)} candles")
            return df
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch historical data: {str(e)}")
    
    def calculate_ema(self, prices, period=5):
        """
        Calculate Exponential Moving Average
        
        Args:
            prices: List or Series of prices
            period: EMA period (default 5)
        """
        prices = pd.Series(prices)
        return prices.ewm(span=period, adjust=False).mean()
    
    def resample_to_5min(self, df):
        """
        Convert 1-minute data to 5-minute candles
        
        Args:
            df: DataFrame with 1-minute candle data
            
        Returns:
            DataFrame: 5-minute candle data
        """
        df_copy = df.copy()
        df_copy.set_index('datetime', inplace=True)
        
        # Resample to 5-minute intervals
        resampled = df_copy.resample('5T').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        # Reset index to get datetime as column
        resampled.reset_index(inplace=True)
        
        # Add timestamp column
        resampled['timestamp'] = resampled['datetime']
        
        return resampled
    
    def get_nifty50_with_ema(self, ema_period=5):
        """
        Get Nifty 50 latest candle data with EMA
        
        Args:
            ema_period: EMA period (default 5)
        
        Returns:
            dict: Latest candle data with EMA value
        """
        try:
            # Try different Nifty 50 instrument keys
            possible_instruments = [
                "NSE_INDEX|Nifty 50",
                "NSE_INDEX|NIFTY 50",
                "NSE_INDEX|Nifty50",
                "NSE_INDEX|NIFTY50"
            ]
            
            df = None
            used_instrument = None
            
            for instrument in possible_instruments:
                try:
                    print(f"🔍 Trying instrument: {instrument}")
                    # Get 1-minute data and convert to 5-minute
                    df_1min = self.get_historical_data(instrument, interval="1minute", days_back=3)
                    df = self.resample_to_5min(df_1min)
                    used_instrument = instrument
                    print(f"✅ Successfully fetched data using: {instrument}")
                    break
                except Exception as e:
                    print(f"❌ Failed with {instrument}: {str(e)}")
                    continue
            
            if df is None or df.empty:
                raise Exception("No data received for any Nifty 50 instrument variant")
            
            # Calculate EMA
            df['ema'] = self.calculate_ema(df['close'], ema_period)
            
            # Get latest candle
            latest = df.iloc[-1]
            
            result = {
                'timestamp': latest['timestamp'],
                'datetime': latest['datetime'],
                'open': float(latest['open']),
                'high': float(latest['high']),
                'low': float(latest['low']),
                'close': float(latest['close']),
                'volume': int(latest['volume']) if pd.notna(latest['volume']) else 0,
                'ema': float(latest['ema']),
                'ema_period': ema_period,
                'instrument': used_instrument
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to get Nifty 50 data with EMA: {str(e)}")
    
    def is_bullish_signal(self, candle_data):
        """
        Check if current candle shows bullish signal
        (Candle is fully above EMA - both low and high are above EMA)
        
        Args:
            candle_data: Dict containing candle data with EMA
        
        Returns:
            bool: True if bullish signal detected
        """
        return candle_data['low'] > candle_data['ema']
    
    def is_bearish_signal(self, candle_data):
        """
        Check if current candle shows bearish signal
        (Candle is fully below EMA - both high and low are below EMA)
        
        Args:
            candle_data: Dict containing candle data with EMA
        
        Returns:
            bool: True if bearish signal detected
        """
        return candle_data['high'] < candle_data['ema']
    
    def get_signal_type(self, candle_data):
        """
        Get signal type for the current candle
        
        Returns:
            str: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        if self.is_bullish_signal(candle_data):
            return 'BULLISH'
        elif self.is_bearish_signal(candle_data):
            return 'BEARISH'
        else:
            return 'NEUTRAL'

def test_client():
    """Test function to verify Upstox client functionality"""
    try:
        print("🧪 Testing Upstox Client...")
        
        client = UpstoxClient()
        data = client.get_nifty50_with_ema()
        
        print("✅ Successfully fetched Nifty 50 data:")
        print(f"   Time: {data['datetime']}")
        print(f"   Close: {data['close']:.2f}")
        print(f"   EMA({data['ema_period']}): {data['ema']:.2f}")
        print(f"   Signal: {client.get_signal_type(data)}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_client()
