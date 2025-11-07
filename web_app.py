from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import json
from time import time
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Global instances
blockchain = None
validator = None
emission_tracker = None
price_engine = None
iot_simulator = None
wallet_manager = None
auth_manager = None

@app.route('/')
def landing():
    """Landing page"""
    return render_template('landing.html')

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Trading dashboard"""
    if 'user' not in session:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/admin')
def admin_panel():
    """Admin panel"""
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    return render_template('admin.html')

@app.route('/company')
def company_panel():
    """Company owner panel"""
    if 'user' not in session or session.get('role') != 'company_owner':
        return redirect(url_for('login_page'))
    return render_template('company.html')

# API Routes
@app.route('/api/login', methods=['POST'])
def api_login():
    """Login API"""
    data = request.json
    result = auth_manager.login(data['username'], data['password'])
    
    if result:
        session['user'] = result['user']['username']
        session['role'] = result['user']['role']
        session['company_symbol'] = result['user'].get('company_symbol')
        
        # Create wallet for trader
        if result['user']['role'] == 'trader':
            if not wallet_manager.get_wallet(result['user']['username']):
                wallet_manager.create_wallet(result['user']['username'], 10000.0)
        
        return jsonify(result)
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout API"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register new trader"""
    data = request.json
    
    try:
        user = auth_manager.create_user(
            data['username'],
            data['password'],
            'trader'
        )
        
        # Create wallet with $10,000
        wallet_manager.create_wallet(data['username'], 10000.0)
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/tokens', methods=['GET'])
def get_tokens():
    """Get all registered tokens"""
    tokens = blockchain.get_all_tokens()
    
    for token_data in tokens:
        token = blockchain.registered_tokens[token_data['symbol']]
        token_data['candle'] = price_engine.get_candle_data(token)
        token_data['chart_data'] = token.get_chart_data(100)
    
    return jsonify(tokens)

@app.route('/api/token/<symbol>', methods=['GET'])
def get_token(symbol):
    """Get specific token details"""
    if symbol not in blockchain.registered_tokens:
        return jsonify({'error': 'Token not found'}), 404
    
    token = blockchain.registered_tokens[symbol]
    token_data = token.to_dict()
    token_data['candle'] = price_engine.get_candle_data(token)
    token_data['chart_data'] = token.get_chart_data(100)
    token_data['emission_chart'] = token.get_emission_chart_data(100)
    
    return jsonify(token_data)

@app.route('/api/wallet', methods=['GET'])
def get_wallet():
    """Get current user's wallet"""
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session.get('user')
    wallet = wallet_manager.get_wallet(username)
    
    if not wallet:
        wallet = wallet_manager.create_wallet(username)
    
    return jsonify(wallet.to_dict(blockchain))

@app.route('/api/wallet/history', methods=['GET'])
def get_wallet_history():
    """Get transaction history"""
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session.get('user')
    wallet = wallet_manager.get_wallet(username)
    
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    return jsonify({
        'transactions': wallet.transaction_history[-50:],
        'total': len(wallet.transaction_history)
    })

@app.route('/api/buy', methods=['POST'])
def buy_tokens():
    """Buy tokens"""
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    username = session.get('user')
    
    try:
        result = wallet_manager.buy_tokens(
            username,
            data['token_symbol'],
            float(data['amount']),
            blockchain
        )
        
        if result['success']:
            blockchain.mine_pending_transactions('SYSTEM')
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/sell', methods=['POST'])
def sell_tokens():
    """Sell tokens"""
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    username = session.get('user')
    
    try:
        result = wallet_manager.sell_tokens(
            username,
            data['token_symbol'],
            float(data['amount']),
            blockchain
        )
        
        if result['success']:
            blockchain.mine_pending_transactions('SYSTEM')
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get user portfolio"""
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    username = session.get('user')
    wallet = wallet_manager.get_wallet(username)
    
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    portfolio = []
    for token_symbol, amount in wallet.token_balances.items():
        if amount > 0 and token_symbol in blockchain.registered_tokens:
            token = blockchain.registered_tokens[token_symbol]
            portfolio.append({
                'symbol': token_symbol,
                'amount': amount,
                'price': token.price,
                'value': amount * token.price,
                'company_name': token.company_name
            })
    
    return jsonify({
        'usd_balance': wallet.usd_balance,
        'holdings': portfolio,
        'total_value': wallet.get_portfolio_value(blockchain)
    })

@app.route('/api/blockchain', methods=['GET'])
def get_blockchain():
    """Get blockchain info"""
    return jsonify({
        'chain_length': len(blockchain.chain),
        'is_valid': blockchain.is_chain_valid(),
        'pending_transactions': len(blockchain.pending_transactions),
        'registered_tokens': len(blockchain.registered_tokens)
    })

@app.route('/api/token/<symbol>/candlestick', methods=['GET'])
def get_candlestick(symbol):
    """Get candlestick data for a token"""
    if symbol not in blockchain.registered_tokens:
        return jsonify({'error': 'Token not found'}), 404
    
    token = blockchain.registered_tokens[symbol]
    period = int(request.args.get('period', 50))
    
    return jsonify({
        'symbol': symbol,
        'candlestick_data': token.get_candlestick_data(period),
        'current_price': token.price,
        'change_24h': token.get_24h_change()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    total_users = len(auth_manager.users)
    total_wallets = len(wallet_manager.wallets)
    total_tokens = len(blockchain.registered_tokens)
    
    total_market_cap = sum(
        token.price * token.circulating_supply 
        for token in blockchain.registered_tokens.values()
    )
    
    return jsonify({
        'total_users': total_users,
        'total_wallets': total_wallets,
        'total_tokens': total_tokens,
        'total_market_cap': total_market_cap,
        'blockchain_length': len(blockchain.chain)
    })

def init_app(bc, val, et, pe, iot, wm, auth):
    """Initialize app with instances"""
    global blockchain, validator, emission_tracker, price_engine, iot_simulator, wallet_manager, auth_manager
    blockchain = bc
    validator = val
    emission_tracker = et
    price_engine = pe
    iot_simulator = iot
    wallet_manager = wm
    auth_manager = auth

if __name__ == '__main__':
    app.run(debug=True, port=5000)