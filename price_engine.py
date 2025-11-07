from typing import Dict
import math

class PriceEngine:
    def __init__(self):
        self.base_volatility = 0.02
        self.emission_impact_factor = 0.5
        self.market_sentiment_factor = 0.3
        self.volume_factor = 0.2
    
    def calculate_price_update(self, token, emission_performance: float, 
                               trading_volume: float = 0, market_sentiment: float = 0.5) -> float:
        """
        Calculate new token price based on emission performance
        
        emission_performance: current_emissions / baseline
            < 1.0 = below baseline (good) = green candle
            > 1.0 = above baseline (bad) = red candle
        """
        current_price = token.price
        
        # 1. Emission Impact
        if emission_performance < 1.0:
            emission_impact = (1.0 - emission_performance) * self.emission_impact_factor
        else:
            emission_impact = -(emission_performance - 1.0) * self.emission_impact_factor
        
        # 2. Market sentiment impact
        sentiment_impact = (market_sentiment - 0.5) * 2 * self.market_sentiment_factor
        
        # 3. Trading volume impact
        volume_impact = math.log1p(trading_volume) * 0.01 * self.volume_factor
        
        # 4. Calculate total price change
        total_impact = emission_impact + sentiment_impact + volume_impact
        
        # Apply price change with bounds
        price_change_percent = total_impact * 100
        price_change_percent = max(min(price_change_percent, 50), -50)
        
        new_price = current_price * (1 + price_change_percent / 100)
        
        # Minimum price floor
        new_price = max(new_price, 0.01)
        
        return round(new_price, 2)
    
    def get_candle_data(self, token, period: str = '1h') -> Dict:
        """Generate candlestick data for charting"""
        price_history = token.price_history[-100:]
        
        if len(price_history) < 2:
            return {
                'open': token.price,
                'high': token.price,
                'low': token.price,
                'close': token.price,
                'color': 'green'
            }
        
        prices = [p[1] for p in price_history]
        open_price = prices[0]
        close_price = prices[-1]
        high_price = max(prices)
        low_price = min(prices)
        
        return {
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'color': 'green' if close_price >= open_price else 'red',
            'change_percent': round(((close_price - open_price) / open_price) * 100, 2)
        }