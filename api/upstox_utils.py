import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import urllib.parse

class UpstoxVercelClient:
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
