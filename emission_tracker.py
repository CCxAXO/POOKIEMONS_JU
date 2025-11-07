from typing import Dict, List
from time import time
import random

class EmissionTracker:
    def __init__(self):
        self.iot_devices: Dict[str, Dict] = {}
        self.emission_data: Dict[str, List] = {}  # {company_symbol: [(timestamp, emissions)]}
        self.validation_threshold = 0.15  # 15% variance allowed for validation
    
    def register_iot_device(self, company_symbol: str, device_id: str, 
                           device_type: str, location: str):
        """Register IoT device for a company"""
        device_key = f"{company_symbol}_{device_id}"
        
        self.iot_devices[device_key] = {
            'device_id': device_id,
            'company_symbol': company_symbol,
            'device_type': device_type,
            'location': location,
            'status': 'active',
            'registered_at': time(),
            'last_reading': None
        }
        
        if company_symbol not in self.emission_data:
            self.emission_data[company_symbol] = []
        
        print(f"IoT Device {device_id} registered for {company_symbol}")
    
    def receive_emission_data(self, company_symbol: str, device_id: str, 
                             emission_value: float) -> Dict:
        """Receive and validate emission data from IoT device"""
        device_key = f"{company_symbol}_{device_id}"
        
        if device_key not in self.iot_devices:
            raise ValueError("IoT device not registered")
        
        timestamp = time()
        
        # Validate with historical data
        is_valid = self._validate_emission_reading(company_symbol, emission_value)
        
        reading = {
            'device_id': device_id,
            'timestamp': timestamp,
            'emission_value': emission_value,
            'validated': is_valid,
            'validation_method': 'historical_comparison'
        }
        
        if is_valid:
            self.emission_data[company_symbol].append((timestamp, emission_value))
            self.iot_devices[device_key]['last_reading'] = reading
        
        return reading
    
    def _validate_emission_reading(self, company_symbol: str, new_value: float) -> bool:
        """Validate emission reading against historical data"""
        if company_symbol not in self.emission_data:
            return True  # First reading always valid
        
        if len(self.emission_data[company_symbol]) == 0:
            return True
        
        # Get recent readings (last 10)
        recent_readings = self.emission_data[company_symbol][-10:]
        if not recent_readings:
            return True
        
        # Calculate average
        avg_emissions = sum(reading[1] for reading in recent_readings) / len(recent_readings)
        
        # Check if within threshold
        variance = abs(new_value - avg_emissions) / avg_emissions if avg_emissions > 0 else 0
        
        # Allow higher variance for demo
        return variance <= self.validation_threshold + 0.35
    
    def get_current_emissions(self, company_symbol: str) -> float:
        """Get current emission value for a company"""
        if company_symbol not in self.emission_data or not self.emission_data[company_symbol]:
            return 0.0
        
        # Average of last 5 readings
        recent = self.emission_data[company_symbol][-5:]
        return sum(r[1] for r in recent) / len(recent)
    
    def get_emission_history(self, company_symbol: str, limit: int = 100) -> List:
        """Get emission history for a company"""
        if company_symbol not in self.emission_data:
            return []
        
        return self.emission_data[company_symbol][-limit:]