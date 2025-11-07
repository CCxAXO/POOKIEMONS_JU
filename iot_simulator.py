import random
from time import time, sleep
from threading import Thread

class IoTSimulator:
    def __init__(self, emission_tracker, blockchain, price_engine):
        self.emission_tracker = emission_tracker
        self.blockchain = blockchain
        self.price_engine = price_engine
        self.running = False
        self.update_interval = 86400  # 24 hours in seconds (daily update)
    
    def simulate_device(self, company_symbol: str, device_id: str, 
                       baseline: float, variance: float = 0.1):
        """Simulate IoT device readings - DAILY updates"""
        while self.running:
            # Generate realistic emission reading
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
                        token.update_price(new_price)
                        
                        print(f"[DAILY UPDATE] {company_symbol}")
                        print(f"  Emissions: {emission_value:.2f} tons (baseline: {baseline:.2f})")
                        print(f"  Price: ${new_price:.2f}")
                        print(f"  Performance: {emission_performance:.2%}")
                        print("-" * 50)
                
            except Exception as e:
                print(f"Error in IoT simulation: {e}")
            
            # Wait for next daily update
            print(f"[{company_symbol}] Next update in 24 hours...")
            sleep(self.update_interval)
    
    def start_simulation(self, companies_config: list):
        """Start simulating multiple companies"""
        self.running = True
        
        for config in companies_config:
            thread = Thread(
                target=self.simulate_device,
                args=(config['symbol'], config['device_id'], 
                      config['baseline'], config.get('variance', 0.1)),
                daemon=True
            )
            thread.start()
        
        print("IoT Simulation started - DAILY emission updates")
    
    def stop_simulation(self):
        """Stop simulation"""
        self.running = False
        print("IoT Simulation stopped")
    
    def set_update_interval(self, hours: int):
        """Change update interval (for testing)"""
        self.update_interval = hours * 3600
        print(f"Update interval set to {hours} hours")