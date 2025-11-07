import json
import os
from time import time
from typing import Dict, List, Optional

class TokenStorage:
    def __init__(self, filename='tokens_data.json'):
        self.filename = filename
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load token data from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    print(f"📂 Loaded token data from {self.filename}")
                    print(f"   Tokens: {list(data.get('tokens', {}).keys())}")
                    return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error loading token data: {e}")
                return {'tokens': {}, 'last_update': 0}
        print(f"📂 No existing token data, creating new file")
        return {'tokens': {}, 'last_update': 0}
    
    def save(self, tokens: Dict):
        """Save token data to file"""
        data = {
            'tokens': {},
            'last_update': time()
        }
        
        for symbol, token in tokens.items():
            # Convert tuples to lists for JSON serialization
            price_history = []
            for item in token.price_history:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    price_history.append([float(item[0]), float(item[1])])
            
            emission_history = []
            for item in token.emission_history:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    emission_history.append([float(item[0]), float(item[1])])
            
            data['tokens'][symbol] = {
                'token_id': token.token_id,
                'company_name': token.company_name,
                'symbol': token.symbol,
                'total_supply': float(token.total_supply),
                'circulating_supply': float(token.circulating_supply),
                'emission_baseline': float(token.emission_baseline),
                'current_emissions': float(token.current_emissions),
                'industry_type': token.industry_type,
                'company_scale': token.company_scale,
                'price': float(token.price),
                'price_history': price_history,
                'emission_history': emission_history,
                'candlestick_data': token.candlestick_data,
                'volume_24h': float(token.volume_24h),
                'is_verified': token.is_verified,
                'created_at': float(token.created_at),
                'owner_address': token.owner_address
            }
        
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Saved {len(tokens)} tokens to {self.filename}")
            
            # Verify save
            for symbol in tokens:
                saved_price = data['tokens'][symbol]['price']
                print(f"   {symbol}: ${saved_price:.2f}")
                
        except IOError as e:
            print(f"❌ Error saving token data: {e}")
    
    def get_token_data(self, symbol: str) -> Optional[Dict]:
        """Get saved data for a specific token"""
        token_data = self.data.get('tokens', {}).get(symbol)
        if token_data:
            print(f"   Loading {symbol}: ${token_data.get('price', 0):.2f}")
        return token_data
    
    def should_update_prices(self) -> bool:
        """Check if 24 hours have passed since last update"""
        last_update = self.data.get('last_update', 0)
        time_passed = time() - last_update
        hours_passed = time_passed / 3600
        
        print(f"⏰ Time since last update: {hours_passed:.1f} hours")
        return time_passed >= 86400  # 24 hours
    
    def get_last_update_time(self) -> float:
        """Get timestamp of last update"""
        return self.data.get('last_update', 0)
    
    def has_saved_data(self) -> bool:
        """Check if any saved token data exists"""
        return bool(self.data.get('tokens', {}))