import json
import os
from time import time
from typing import Dict, List, Optional

class DataStorage:
    def __init__(self, storage_dir='data'):
        self.storage_dir = storage_dir
        
        # Create data directory if it doesn't exist
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            print(f"✓ Created data storage directory: {storage_dir}")
    
    def save_token_data(self, token_symbol: str, data: Dict):
        """Save token data to JSON file"""
        filename = os.path.join(self.storage_dir, f'{token_symbol}.json')
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Saved data for {token_symbol}")
        except Exception as e:
            print(f"Error saving {token_symbol}: {e}")
    
    def load_token_data(self, token_symbol: str) -> Optional[Dict]:
        """Load token data from JSON file"""
        filename = os.path.join(self.storage_dir, f'{token_symbol}.json')
        
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"✓ Loaded data for {token_symbol}")
            return data
        except Exception as e:
            print(f"Error loading {token_symbol}: {e}")
            return None
    
    def token_data_exists(self, token_symbol: str) -> bool:
        """Check if token data file exists"""
        filename = os.path.join(self.storage_dir, f'{token_symbol}.json')
        return os.path.exists(filename)
    
    def delete_token_data(self, token_symbol: str):
        """Delete token data file"""
        filename = os.path.join(self.storage_dir, f'{token_symbol}.json')
        
        if os.path.exists(filename):
            os.remove(filename)
            print(f"✓ Deleted data for {token_symbol}")
    
    def save_all_tokens(self, tokens: Dict):
        """Save all token data"""
        for symbol, token in tokens.items():
            self.save_token_data(symbol, token.to_storage_dict())
    
    def get_all_token_files(self) -> List[str]:
        """Get list of all saved token symbols"""
        files = [f.replace('.json', '') for f in os.listdir(self.storage_dir) 
                 if f.endswith('.json')]
        return files


# Global storage instance
data_storage = DataStorage()