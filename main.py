from blockchain import CarbonCoinBlockchain
from company_token import CompanyToken
from validator import CompanyValidator
from emission_tracker import EmissionTracker
from price_engine import PriceEngine
from iot_simulator import IoTSimulator
from wallet import WalletManager
from auth import AuthManager
from web_app import app, init_app

def setup_demo_data(blockchain, validator, emission_tracker, auth_manager, wallet_manager):
    """Setup demo companies and tokens"""
    
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
    
    for company in demo_companies:
        app_id = validator.submit_application(company)
        validator.auto_validate_demo(app_id)
        
        token = CompanyToken(
            company_name=company['company_name'],
            symbol=company['symbol'],
            initial_supply=company['initial_supply'],
            emission_baseline=company['emission_baseline'],
            industry_type=company['industry_type'],
            company_scale=company['company_scale']
        )
        token.is_verified = True
        token.owner_address = f"WALLET_{company['symbol']}"
        
        blockchain.register_token(token)
        token.mint(company['initial_supply'] * 0.3, token.owner_address, blockchain)
        
        device_id = f"IOT_{company['symbol']}_001"
        emission_tracker.register_iot_device(
            company['symbol'],
            device_id,
            "CO2_SENSOR",
            company['location']
        )
        
        # Create company owner account
        auth_manager.create_user(
            f"owner_{company['symbol'].lower()}",
            "owner123",
            "company_owner",
            company['symbol']
        )
        
        iot_configs.append({
            'symbol': company['symbol'],
            'device_id': device_id,
            'baseline': company['emission_baseline'],
            'variance': 0.15
        })
    
    blockchain.mine_pending_transactions('GENESIS')
    print(f"\n✓ Setup complete: {len(demo_companies)} companies registered")
    
    # Create demo trader
    auth_manager.create_user('trader1', 'trader123', 'trader')
    wallet_manager.create_wallet('trader1', 10000.0)
    
    return iot_configs

def main():
    print("=" * 60)
    print("🌍 CarbonCoin Trading Platform - Initializing...")
    print("=" * 60)
    
    # Initialize components
    blockchain = CarbonCoinBlockchain(difficulty=3)
    validator = CompanyValidator()
    emission_tracker = EmissionTracker()
    price_engine = PriceEngine()
    iot_simulator = IoTSimulator(emission_tracker, blockchain, price_engine)
    wallet_manager = WalletManager()
    auth_manager = AuthManager()
    
    # Set to 24 hours for production (or 1 hour for testing)
    iot_simulator.set_update_interval(24)
    
    # Setup demo data
    print("\n📝 Setting up demo companies...")
    iot_configs = setup_demo_data(blockchain, validator, emission_tracker, auth_manager, wallet_manager)
    
    # Start IoT simulation
    print("\n🔌 Starting IoT emission tracking (Daily updates)...")
    iot_simulator.start_simulation(iot_configs)
    
    # Initialize Flask app
    init_app(blockchain, validator, emission_tracker, price_engine, iot_simulator, wallet_manager, auth_manager)
    
    print("\n" + "=" * 60)
    print("✓ CarbonCoin Trading Platform is LIVE!")
    print("=" * 60)
    print("\n📊 Access the platform:")
    print("   Landing Page: http://localhost:5000")
    print("   Login Page: http://localhost:5000/login")
    print("\n🔐 Demo Accounts:")
    print("   Admin: admin / admin123")
    print("   Trader: trader1 / trader123")
    print("   Company Owners: owner_gti / owner123")
    print("\n💡 Features:")
    print("   • Beautiful landing page with animations")
    print("   • Login system for admin, owners, and traders")
    print("   • Historical price charts (100 days)")
    print("   • Real-time emission tracking")
    print("   • Buy/Sell with $10,000 demo money")
    print("   • 1% transaction fee")
    print("\n⚠️  Press Ctrl+C to stop\n")
    
    # Run Flask app
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()