from blockchain import CarbonCoinBlockchain
from company_token import CompanyToken
from validator import CompanyValidator
from emission_tracker import EmissionTracker
from price_engine import PriceEngine
from iot_simulator import IoTSimulator
from wallet import WalletManager
from auth import AuthManager
from web_app import app, init_app
from token_storage import TokenStorage
import atexit  # ⭐ ADD THIS
import signal  # ⭐ ADD THIS
import sys     # ⭐ ADD THIS

# Global variable to store tokens and storage
token_storage = None
registered_tokens = {}  # Store tokens here instead of blockchain

def save_on_exit():
    """Save token data when server stops"""
    global token_storage, registered_tokens
    
    if token_storage and registered_tokens:
        print("\n💾 Saving token data before shutdown...")
        try:
            token_storage.save(registered_tokens)
            print("✓ Token data saved successfully")
        except Exception as e:
            print(f"❌ Error saving tokens: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    save_on_exit()
    sys.exit(0)

def setup_demo_data(blockchain, validator, emission_tracker, storage):
    """Setup demo companies and tokens"""
    global registered_tokens
    
    demo_companies = [
        {
            'company_name': 'GreenTech Industries',
            'symbol': 'GTI',
            'industry_type': 'Manufacturing',
            'company_scale': 'large',
            'emission_baseline': 1000.0,
            'initial_supply': 1000000,
            'location': 'Factory A - California'
        },
        {
            'company_name': 'EcoSteel Corp',
            'symbol': 'ESC',
            'industry_type': 'Steel Production',
            'company_scale': 'large',
            'emission_baseline': 2500.0,
            'initial_supply': 800000,
            'location': 'Steel Mill - Pittsburgh'
        },
        {
            'company_name': 'CleanEnergy Solutions',
            'symbol': 'CES',
            'industry_type': 'Energy',
            'company_scale': 'medium',
            'emission_baseline': 500.0,
            'initial_supply': 500000,
            'location': 'Power Plant - Texas'
        },
        {
            'company_name': 'SustainableTextiles',
            'symbol': 'STX',
            'industry_type': 'Textile',
            'company_scale': 'medium',
            'emission_baseline': 300.0,
            'initial_supply': 600000,
            'location': 'Textile Factory - India'
        }
    ]
    
    iot_configs = []
    
    print(f"\n{'='*60}")
    print("📝 Setting up demo companies...")
    print(f"{'='*60}")
    
    for company in demo_companies:
        symbol = company['symbol']
        
        # Check if token already exists in storage
        saved_data = storage.get_token_data(symbol)
        
        if saved_data:
            print(f"\n✓ {company['company_name']} ({symbol})")
            print(f"  Loading from saved data...")
            token = CompanyToken(
                company_name=company['company_name'],
                symbol=symbol,
                initial_supply=company['initial_supply'],
                emission_baseline=company['emission_baseline'],
                industry_type=company['industry_type'],
                company_scale=company['company_scale'],
                saved_data=saved_data  # Load from saved data
            )
            print(f"  Price: ${token.price:.2f} | Candles: {len(token.candlestick_data)}")
        else:
            print(f"\n✓ {company['company_name']} ({symbol})")
            print(f"  Creating new token with historical data...")
            
            app_id = validator.submit_application(company)
            validator.auto_validate_demo(app_id)
            
            token = CompanyToken(
                company_name=company['company_name'],
                symbol=symbol,
                initial_supply=company['initial_supply'],
                emission_baseline=company['emission_baseline'],
                industry_type=company['industry_type'],
                company_scale=company['company_scale']
            )
            token.is_verified = True
            token.owner_address = f"WALLET_{symbol}"
            token.mint(company['initial_supply'] * 0.3, token.owner_address, blockchain)
            
            print(f"  Price: ${token.price:.2f} | Candles: {len(token.candlestick_data)}")
        
        blockchain.register_token(token)
        registered_tokens[symbol] = token  # Store in global dict
        
        device_id = f"IOT_{symbol}_001"
        emission_tracker.register_iot_device(
            symbol,
            device_id,
            "CO2_SENSOR",
            company['location']
        )
        
        iot_configs.append({
            'symbol': symbol,
            'device_id': device_id,
            'baseline': company['emission_baseline'],
            'variance': 0.15
        })
    
    # Save all tokens immediately after setup
    storage.save(registered_tokens)
    
    blockchain.mine_pending_transactions('GENESIS')
    
    print(f"\n{'='*60}")
    print(f"✓ Setup complete: {len(demo_companies)} companies registered")
    print(f"{'='*60}")
    
    # Check if prices should update
    if storage.should_update_prices():
        print("\n⏰ 24 hours passed - prices will update on next cycle")
    else:
        from datetime import datetime, timedelta
        last_update = datetime.fromtimestamp(storage.get_last_update_time())
        next_update = last_update + timedelta(days=1)
        print(f"⏰ Next price update: {next_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return iot_configs

def main():
    global token_storage, registered_tokens
    
    # Register exit handlers
    atexit.register(save_on_exit)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("🌍 CarbonCoin Trading Platform - Initializing...")
    print("=" * 60)
    
    try:
        # Initialize components
        blockchain = CarbonCoinBlockchain(difficulty=2)
        validator = CompanyValidator()
        emission_tracker = EmissionTracker()
        price_engine = PriceEngine()
        token_storage = TokenStorage()
        iot_simulator = IoTSimulator(emission_tracker, blockchain, price_engine)
        
        # Pass token_storage to IoT simulator
        iot_simulator.token_storage = token_storage
        
        wallet_manager = WalletManager()
        auth_manager = AuthManager()
        
        # Set to 24 hours for production
        iot_simulator.set_update_interval(24)
        
        # Setup demo data
        iot_configs = setup_demo_data(blockchain, validator, emission_tracker, token_storage)
        
        # Start IoT simulation
        print("\n🔌 Starting IoT emission tracking...")
        iot_simulator.start_simulation(iot_configs)
        
        # Initialize Flask app
        init_app(blockchain, validator, emission_tracker, price_engine, iot_simulator, wallet_manager, auth_manager)
        
        print("\n" + "=" * 60)
        print("✓ CarbonCoin Trading Platform is LIVE!")
        print("=" * 60)
        print("\n📊 Access the platform:")
        print("   Landing: http://localhost:5000")
        print("   Login: http://localhost:5000/login")
        print("   Dashboard: http://localhost:5000/dashboard")
        print("   Admin: http://localhost:5000/admin")
        print("\n🔐 Demo Accounts:")
        print("   Admin: admin / admin123")
        print("   (Register new traders on login page)")
        print("\n💡 Features:")
        print("   • Persistent token data (auto-saves on shutdown)")
        print("   • Prices update once every 24 hours")
        print("   • Individual token pages with candlestick charts")
        print("   • Green/Red candles based on price movement")
        print("   • Admin can create/delete tokens")
        print("   • Buy/Sell with real-time updates")
        print("\n⚠️  Press Ctrl+C to stop (data will auto-save)\n")
        
        # Run Flask app
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        save_on_exit()

if __name__ == '__main__':
    main()