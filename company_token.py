from typing import Dict, List, Optional
from time import time
import uuid
import random

class CompanyToken:
    def __init__(self, company_name: str, symbol: str, 
                 initial_supply: float, emission_baseline: float,
                 industry_type: str, company_scale: str,
                 saved_data: Optional[Dict] = None):
        
        if saved_data:
            # Load from saved data
            self._load_from_saved(saved_data)
        else:
            # Create new token
            self.token_id = str(uuid.uuid4())
            self.company_name = company_name
            self.symbol = symbol.upper()
            self.total_supply = initial_supply
            self.circulating_supply = 0
            self.emission_baseline = emission_baseline
            self.current_emissions = emission_baseline
            self.industry_type = industry_type
            self.company_scale = company_scale
            self.price = 100.0
            self.price_history = []
            self.emission_history = []
            self.candlestick_data = []
            self.volume_24h = 0
            self.trades = []
            self.is_verified = False
            self.created_at = time()
            self.owner_address = None
            
            # Generate historical data ONLY for new tokens
            self._generate_historical_data()
    
    def _load_from_saved(self, data: Dict):
        """Load token from saved data - NO MODIFICATIONS"""
        self.token_id = data.get('token_id', str(uuid.uuid4()))
        self.company_name = data['company_name']
        self.symbol = data['symbol']
        self.total_supply = data['total_supply']
        self.circulating_supply = data.get('circulating_supply', 0)
        self.emission_baseline = data['emission_baseline']
        self.current_emissions = data.get('current_emissions', data['emission_baseline'])
        self.industry_type = data['industry_type']
        self.company_scale = data['company_scale']
        self.price = data.get('price', 100.0)
        
        # Convert lists back to tuples (JSON stores tuples as lists)
        price_history_data = data.get('price_history', [])
        self.price_history = [tuple(item) if isinstance(item, list) else item 
                              for item in price_history_data]
        
        emission_history_data = data.get('emission_history', [])
        self.emission_history = [tuple(item) if isinstance(item, list) else item 
                                 for item in emission_history_data]
        
        self.candlestick_data = data.get('candlestick_data', [])
        self.volume_24h = data.get('volume_24h', 0)
        self.trades = []
        self.is_verified = data.get('is_verified', False)
        self.created_at = data.get('created_at', time())
        self.owner_address = data.get('owner_address')
        
        # Verify data integrity
        if self.candlestick_data:
            last_candle = self.candlestick_data[-1]
            print(f"      Loaded: {len(self.candlestick_data)} candles, Last: ${last_candle['close']:.2f}")
    
    def _generate_historical_data(self):
        """Generate realistic historical price and emission data with OHLC"""
        base_price = 100.0
        base_emission = self.emission_baseline
        current_time = time()
        
        # Generate 100 days of historical data
        for i in range(100, 0, -1):
            timestamp = current_time - (i * 86400)  # 1 day intervals
            
            # OHLC for candlestick
            open_price = base_price
            daily_change = random.uniform(-0.08, 0.08)  # ±8% daily
            close_price = open_price * (1 + daily_change)
            
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.05)
            low_price = min(open_price, close_price) * random.uniform(0.95, 1.0)
            
            volume = random.uniform(1000, 10000)
            
            self.candlestick_data.append({
                'timestamp': timestamp,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': round(volume, 2)
            })
            
            base_price = close_price
            
            # Simple price history
            self.price_history.append((timestamp, round(close_price, 2)))
            
            # Emission data
            emission_change = random.uniform(-0.1, 0.1)
            base_emission = base_emission * (1 + emission_change)
            self.emission_history.append((timestamp, round(base_emission, 2)))
        
        # Set current values
        self.price = self.candlestick_data[-1]['close']
        self.current_emissions = self.emission_history[-1][1]
        
        print(f"      Generated: {len(self.candlestick_data)} candles, Current: ${self.price:.2f}")
    
    def update_emissions(self, new_emissions: float):
        """Update current CO2 emissions"""
        self.current_emissions = new_emissions
        self.emission_history.append((time(), new_emissions))
        
        if len(self.emission_history) > 100:
            self.emission_history = self.emission_history[-100:]
    
    def update_price(self, new_price: float, force: bool = False):
        """Update token price and candlestick"""
        current_time = time()
        
        # Prevent price updates if not forced and less than 24h since last candle
        if not force and self.candlestick_data:
            last_candle = self.candlestick_data[-1]
            time_diff = current_time - last_candle['timestamp']
            
            if time_diff < 86400:  # Less than 24 hours
                # Only update the current candle, don't change base price
                last_candle['high'] = max(last_candle['high'], new_price)
                last_candle['low'] = min(last_candle['low'], new_price)
                last_candle['close'] = new_price
                self.price = new_price
                return
        
        # Update price history
        self.price = new_price
        self.price_history.append((current_time, new_price))
        
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
        
        # Update candlestick
        if self.candlestick_data:
            last_candle = self.candlestick_data[-1]
            time_diff = current_time - last_candle['timestamp']
            
            if time_diff >= 86400:  # New day
                new_candle = {
                    'timestamp': current_time,
                    'open': last_candle['close'],
                    'high': new_price,
                    'low': new_price,
                    'close': new_price,
                    'volume': 0
                }
                self.candlestick_data.append(new_candle)
                
                if len(self.candlestick_data) > 100:
                    self.candlestick_data = self.candlestick_data[-100:]
            else:
                # Update current candle
                last_candle['high'] = max(last_candle['high'], new_price)
                last_candle['low'] = min(last_candle['low'], new_price)
                last_candle['close'] = new_price
    
    def add_trade(self, amount: float, price: float, trade_type: str):
        """Record a trade"""
        self.trades.append({
            'timestamp': time(),
            'amount': amount,
            'price': price,
            'type': trade_type
        })
        self.volume_24h += amount * price
        
        if self.candlestick_data:
            self.candlestick_data[-1]['volume'] += amount
    
    def get_emission_performance(self) -> float:
        """Calculate emission performance ratio"""
        if self.emission_baseline == 0:
            return 1.0
        return self.current_emissions / self.emission_baseline
    
    def get_chart_data(self, period: int = 100) -> List[Dict]:
        """Get price chart data"""
        return [
            {
                'timestamp': ts,
                'price': price,
                'date': self._format_date(ts)
            }
            for ts, price in self.price_history[-period:]
        ]
    
    def get_candlestick_data(self, period: int = 50) -> List[Dict]:
        """Get candlestick chart data"""
        data = []
        for candle in self.candlestick_data[-period:]:
            data.append({
                'x': candle['timestamp'] * 1000,  # Convert to milliseconds for Chart.js
                'o': candle['open'],
                'h': candle['high'],
                'l': candle['low'],
                'c': candle['close'],
                'volume': candle['volume']
            })
        return data
    
    def get_emission_chart_data(self, period: int = 100) -> List[Dict]:
        """Get emission chart data"""
        return [
            {
                'timestamp': ts,
                'emissions': em,
                'date': self._format_date(ts)
            }
            for ts, em in self.emission_history[-period:]
        ]
    
    def _format_date(self, timestamp: float) -> str:
        """Format timestamp to readable date"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    
    def mint(self, amount: float, to_address: str, blockchain) -> bool:
        """Mint new tokens"""
        if self.circulating_supply + amount > self.total_supply:
            raise ValueError("Exceeds total supply")
        
        transaction = {
            'type': 'MINT',
            'from_address': 'MINT',
            'to_address': to_address,
            'amount': amount,
            'token_symbol': self.symbol
        }
        
        blockchain.create_transaction(transaction)
        self.circulating_supply += amount
        return True
    
    def get_24h_change(self) -> Dict:
        """Get 24h price change"""
        if not self.candlestick_data or len(self.candlestick_data) < 2:
            return {'change': 0, 'change_percent': 0}
        
        try:
            yesterday = self.candlestick_data[-2]['close']
            today = self.candlestick_data[-1]['close']
            change = today - yesterday
            change_percent = (change / yesterday) * 100 if yesterday > 0 else 0
            
            return {
                'change': round(change, 2),
                'change_percent': round(change_percent, 2)
            }
        except (KeyError, IndexError, ZeroDivisionError):
            return {'change': 0, 'change_percent': 0}
    
    def to_dict(self) -> Dict:
        change_data = self.get_24h_change()
        
        return {
            'token_id': self.token_id,
            'company_name': self.company_name,
            'symbol': self.symbol,
            'total_supply': self.total_supply,
            'circulating_supply': self.circulating_supply,
            'emission_baseline': self.emission_baseline,
            'current_emissions': self.current_emissions,
            'industry_type': self.industry_type,
            'company_scale': self.company_scale,
            'price': self.price,
            'volume_24h': self.volume_24h,
            'change_24h': change_data['change'],
            'change_percent_24h': change_data['change_percent'],
            'emission_performance': self.get_emission_performance(),
            'is_verified': self.is_verified,
            'created_at': self.created_at
        }