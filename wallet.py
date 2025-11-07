from typing import Dict
import uuid
from time import time

class Wallet:
    def __init__(self, username: str, initial_balance: float = 10000.0):
        self.address = str(uuid.uuid4())
        self.username = username
        self.usd_balance = initial_balance  # Fake money for testing
        self.token_balances: Dict[str, float] = {}  # {token_symbol: amount}
        self.transaction_history = []
        self.created_at = time()
    
    def get_balance(self, token_symbol: str = None) -> float:
        """Get balance (USD or specific token)"""
        if token_symbol is None:
            return self.usd_balance
        return self.token_balances.get(token_symbol, 0.0)
    
    def add_usd(self, amount: float):
        """Add USD to wallet"""
        self.usd_balance += amount
        self.transaction_history.append({
            'timestamp': time(),
            'type': 'DEPOSIT',
            'amount': amount,
            'currency': 'USD'
        })
    
    def deduct_usd(self, amount: float) -> bool:
        """Deduct USD from wallet"""
        if self.usd_balance < amount:
            return False
        self.usd_balance -= amount
        return True
    
    def add_tokens(self, token_symbol: str, amount: float):
        """Add tokens to wallet"""
        if token_symbol not in self.token_balances:
            self.token_balances[token_symbol] = 0
        self.token_balances[token_symbol] += amount
    
    def deduct_tokens(self, token_symbol: str, amount: float) -> bool:
        """Deduct tokens from wallet"""
        if token_symbol not in self.token_balances:
            return False
        if self.token_balances[token_symbol] < amount:
            return False
        self.token_balances[token_symbol] -= amount
        return True
    
    def record_trade(self, trade_type: str, token_symbol: str, 
                     amount: float, price: float, fee: float):
        """Record a trade in history"""
        self.transaction_history.append({
            'timestamp': time(),
            'type': trade_type,
            'token_symbol': token_symbol,
            'amount': amount,
            'price': price,
            'total': amount * price,
            'fee': fee
        })
    
    def get_portfolio_value(self, blockchain) -> float:
        """Calculate total portfolio value"""
        total = self.usd_balance
        
        for token_symbol, amount in self.token_balances.items():
            if token_symbol in blockchain.registered_tokens:
                token = blockchain.registered_tokens[token_symbol]
                total += amount * token.price
        
        return total
    
    def to_dict(self, blockchain=None) -> Dict:
        portfolio_value = self.get_portfolio_value(blockchain) if blockchain else self.usd_balance
        
        return {
            'address': self.address,
            'username': self.username,
            'usd_balance': round(self.usd_balance, 2),
            'token_balances': self.token_balances,
            'portfolio_value': round(portfolio_value, 2),
            'transaction_count': len(self.transaction_history),
            'created_at': self.created_at
        }


class WalletManager:
    def __init__(self):
        self.wallets: Dict[str, Wallet] = {}
        self.transaction_fee = 0.01  # 1% fee
    
    def create_wallet(self, username: str, initial_balance: float = 10000.0) -> Wallet:
        """Create a new wallet"""
        if username in self.wallets:
            return self.wallets[username]
        
        wallet = Wallet(username, initial_balance)
        self.wallets[username] = wallet
        print(f"Wallet created for {username} with ${initial_balance}")
        return wallet
    
    def get_wallet(self, username: str) -> Wallet:
        """Get wallet by username"""
        return self.wallets.get(username)
    
    def buy_tokens(self, username: str, token_symbol: str, 
                   amount: float, blockchain) -> Dict:
        """Buy tokens with USD"""
        wallet = self.get_wallet(username)
        if not wallet:
            return {'success': False, 'error': 'Wallet not found'}
        
        if token_symbol not in blockchain.registered_tokens:
            return {'success': False, 'error': 'Token not found'}
        
        token = blockchain.registered_tokens[token_symbol]
        
        # Calculate costs
        cost = amount * token.price
        fee = cost * self.transaction_fee
        total_cost = cost + fee
        
        # Check balance
        if wallet.usd_balance < total_cost:
            return {
                'success': False, 
                'error': f'Insufficient funds. Need ${total_cost:.2f}, have ${wallet.usd_balance:.2f}'
            }
        
        # Execute trade
        wallet.deduct_usd(total_cost)
        wallet.add_tokens(token_symbol, amount)
        wallet.record_trade('BUY', token_symbol, amount, token.price, fee)
        
        # Update token stats
        token.add_trade(amount, token.price, 'BUY')
        
        # Create blockchain transaction
        blockchain.create_transaction({
            'type': 'BUY',
            'from_address': wallet.address,
            'to_address': wallet.address,
            'amount': amount,
            'token_symbol': token_symbol,
            'price': token.price,
            'fee': fee
        })
        
        return {
            'success': True,
            'amount': amount,
            'price': token.price,
            'cost': cost,
            'fee': fee,
            'total': total_cost,
            'new_balance': wallet.usd_balance,
            'new_token_balance': wallet.get_balance(token_symbol)
        }
    
    def sell_tokens(self, username: str, token_symbol: str, 
                    amount: float, blockchain) -> Dict:
        """Sell tokens for USD"""
        wallet = self.get_wallet(username)
        if not wallet:
            return {'success': False, 'error': 'Wallet not found'}
        
        if token_symbol not in blockchain.registered_tokens:
            return {'success': False, 'error': 'Token not found'}
        
        token = blockchain.registered_tokens[token_symbol]
        
        # Check token balance
        if wallet.get_balance(token_symbol) < amount:
            return {
                'success': False, 
                'error': f'Insufficient tokens. Need {amount}, have {wallet.get_balance(token_symbol)}'
            }
        
        # Calculate proceeds
        proceeds = amount * token.price
        fee = proceeds * self.transaction_fee
        net_proceeds = proceeds - fee
        
        # Execute trade
        wallet.deduct_tokens(token_symbol, amount)
        wallet.add_usd(net_proceeds)
        wallet.record_trade('SELL', token_symbol, amount, token.price, fee)
        
        # Update token stats
        token.add_trade(amount, token.price, 'SELL')
        
        # Create blockchain transaction
        blockchain.create_transaction({
            'type': 'SELL',
            'from_address': wallet.address,
            'to_address': wallet.address,
            'amount': amount,
            'token_symbol': token_symbol,
            'price': token.price,
            'fee': fee
        })
        
        return {
            'success': True,
            'amount': amount,
            'price': token.price,
            'proceeds': proceeds,
            'fee': fee,
            'net_proceeds': net_proceeds,
            'new_balance': wallet.usd_balance,
            'new_token_balance': wallet.get_balance(token_symbol)
        }