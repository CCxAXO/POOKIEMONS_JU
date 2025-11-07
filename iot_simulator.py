import random
from time import time, sleep
from threading import Thread
from datetime import datetime

class IoTSimulator:
    def __init__(self, emission_tracker, blockchain, price_engine):
        self.emission_tracker = emission_tracker
        self.blockchain = blockchain
        self.price_engine = price_engine
        self.running = False
        self.update_interval = 86400  # 24 hours in seconds (daily update)
        self.token_storage = None  # Will be set from main.py
        self.last_update_time = {}  # Track last update per symbol
    
    def simulate_device(self, company_symbol: str, device_id: str, 
                       baseline: float, variance: float = 0.1):
        """Simulate IoT device readings - DAILY updates ONLY"""
        
        # Initialize last update time
        if company_symbol not in self.last_update_time:
            if self.token_storage:
                self.last_update_time[company_symbol] = self.token_storage.get_last_update_time()
            else:
                self.last_update_time[company_symbol] = time()
        
        while self.running:
            # Check if 24 hours have passed since last update
            time_since_last_update = time() - self.last_update_time[company_symbol]
            
            if time_since_last_update < self.update_interval:
                # Calculate remaining time to wait
                wait_time = self.update_interval - time_since_last_update
                hours_remaining = wait_time / 3600
                
                print(f"[{company_symbol}] Skipping update - {hours_remaining:.1f} hours until next update")
                
                # Sleep for the remaining time (but check every hour if still running)
                sleep_chunk = min(3600, wait_time)  # Sleep in 1-hour chunks
                sleep(sleep_chunk)
                continue
            
            # 24 hours have passed - perform update
            variation = random.uniform(-variance, variance)
            emission_value = baseline * (1 + variation)
            emission_value = max(0, emission_value)
            
            try:
                # Send reading to tracker
                reading = self.emission_tracker.receive_emission_data(
                    company_symbol, device_id, emission_value
                )
                
                if reading['validated']:
                    # Update token emissions
                    token = self.blockchain.registered_tokens.get(company_symbol)
                    if token:
                        token.update_emissions(emission_value)
                        
                        # Update price based on emissions
                        emission_performance = token.get_emission_performance()
                        new_price = self.price_engine.calculate_price_update(
                            token, emission_performance
                        )
                        token.update_price(new_price, force=True)  # Force update after 24h
                        
                        # Update last update time
                        self.last_update_time[company_symbol] = time()
                        
                        # Save to storage
                        if self.token_storage:
                            from main import registered_tokens
                            self.token_storage.save(registered_tokens)
                        
                        print(f"\n{'='*60}")
                        print(f"[DAILY UPDATE] {company_symbol} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"{'='*60}")
                        print(f"  Emissions: {emission_value:.2f} tons (baseline: {baseline:.2f})")
                        print(f"  Price: ${token.price:.2f} → ${new_price:.2f}")
                        print(f"  Performance: {emission_performance:.2%}")
                        print(f"  Next update: {datetime.fromtimestamp(time() + self.update_interval).strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"{'='*60}\n")
                
            except Exception as e:
                print(f"❌ Error in IoT simulation for {company_symbol}: {e}")
                import traceback
                traceback.print_exc()
            
            # Wait for next daily update
            sleep(self.update_interval)
    
    def start_simulation(self, companies_config: list):
        """Start simulating multiple companies"""
        self.running = True
        
        print(f"\n{'='*60}")
        print("🔌 IoT Simulation Configuration")
        print(f"{'='*60}")
        print(f"Update Interval: {self.update_interval / 3600:.0f} hours")
        print(f"Companies: {len(companies_config)}")
        
        for config in companies_config:
            thread = Thread(
                target=self.simulate_device,
                args=(config['symbol'], config['device_id'], 
                      config['baseline'], config.get('variance', 0.1)),
                daemon=True
            )
            thread.start()
            print(f"  ✓ {config['symbol']} - Device {config['device_id']}")
        
        print(f"{'='*60}\n")
        print("✓ IoT Simulation started - DAILY emission updates only")
        print("  (Prices will NOT change until 24 hours have passed)\n")
    
    def stop_simulation(self):
        """Stop simulation"""
        self.running = False
        print("IoT Simulation stopped")
    
    def set_update_interval(self, hours: int):
        """Change update interval (for testing)"""
        self.update_interval = hours * 3600
        print(f"Update interval set to {hours} hours ({hours * 3600} seconds)")
    
    def force_update_all(self):
        """Force immediate update for all tokens (admin function)"""
        print("\n⚠️  FORCING IMMEDIATE UPDATE FOR ALL TOKENS")
        self.last_update_time = {}  # Reset all timers