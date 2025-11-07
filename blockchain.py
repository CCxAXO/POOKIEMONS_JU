import hashlib
import json
from time import time
from typing import List, Dict, Any
import uuid

class Block:
    def __init__(self, index: int, transactions: List[Dict], timestamp: float, 
                 previous_hash: str, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }


class CarbonCoinBlockchain:
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.difficulty = difficulty
        self.mining_reward = 10
        self.registered_tokens: Dict[str, Any] = {}
        self.balances: Dict[str, Dict[str, float]] = {}
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(0, [], time(), "0")
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        return self.chain[-1]
    
    def mine_pending_transactions(self, miner_address: str):
        """Mine pending transactions and add to blockchain"""
        if not self.pending_transactions:
            return False
        
        block = Block(
            len(self.chain),
            self.pending_transactions,
            time(),
            self.get_latest_block().hash
        )
        
        # Proof of Work
        while not block.hash.startswith('0' * self.difficulty):
            block.nonce += 1
            block.hash = block.calculate_hash()
        
        print(f"Block mined: {block.hash}")
        self.chain.append(block)
        
        # Process transactions
        for tx in self.pending_transactions:
            self._update_balances(tx)
        
        # Reset pending transactions
        self.pending_transactions = []
        return True
    
    def create_transaction(self, transaction: Dict) -> str:
        """Add a new transaction to pending transactions"""
        transaction['id'] = str(uuid.uuid4())
        transaction['timestamp'] = time()
        
        # Validate transaction
        if not self._validate_transaction(transaction):
            raise ValueError("Invalid transaction: Insufficient balance or invalid data")
        
        self.pending_transactions.append(transaction)
        return transaction['id']
    
    def _validate_transaction(self, transaction: Dict) -> bool:
        """Validate transaction has required fields and sufficient balance"""
        required_fields = ['from_address', 'to_address', 'amount', 'token_symbol']
        
        if not all(field in transaction for field in required_fields):
            print(f"Missing required fields in transaction")
            return False
        
        # Skip validation for minting and system transactions
        if transaction['from_address'] in ['MINT', 'SYSTEM']:
            return True
        
        # For BUY transactions, skip token balance check (buying with USD)
        if transaction.get('type') == 'BUY':
            return True
        
        # For SELL transactions, check token balance
        if transaction.get('type') == 'SELL':
            from_addr = transaction['from_address']
            token = transaction['token_symbol']
            amount = transaction['amount']
            
            if from_addr not in self.balances:
                print(f"Address {from_addr} not found in balances")
                return False
            
            if token not in self.balances[from_addr]:
                print(f"Token {token} not found for address {from_addr}")
                return False
            
            if self.balances[from_addr][token] < amount:
                print(f"Insufficient balance: have {self.balances[from_addr][token]}, need {amount}")
                return False
        
        return True
    
    def _update_balances(self, transaction: Dict):
        """Update balances after transaction is mined"""
        from_addr = transaction['from_address']
        to_addr = transaction['to_address']
        token = transaction['token_symbol']
        amount = transaction['amount']
        
        # Initialize balances if needed
        if to_addr not in self.balances:
            self.balances[to_addr] = {}
        if token not in self.balances[to_addr]:
            self.balances[to_addr][token] = 0
        
        # For BUY transactions, just add tokens to buyer
        if transaction.get('type') == 'BUY':
            self.balances[to_addr][token] += amount
        
        # For SELL transactions, deduct from seller
        elif transaction.get('type') == 'SELL':
            if from_addr in self.balances and token in self.balances[from_addr]:
                self.balances[from_addr][token] -= amount
        
        # For regular transfers
        elif from_addr not in ['MINT', 'SYSTEM']:
            if from_addr not in self.balances:
                self.balances[from_addr] = {}
            if token not in self.balances[from_addr]:
                self.balances[from_addr][token] = 0
            
            self.balances[from_addr][token] -= amount
            self.balances[to_addr][token] += amount
        else:
            # MINT or SYSTEM
            self.balances[to_addr][token] += amount
    
    def get_balance(self, address: str, token_symbol: str) -> float:
        """Get balance of specific token for an address"""
        if address not in self.balances:
            return 0.0
        return self.balances[address].get(token_symbol, 0.0)
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
            
            if not current_block.hash.startswith('0' * self.difficulty):
                return False
        
        return True
    
    def register_token(self, token):
        """Register a new company token on the blockchain"""
        if token.symbol in self.registered_tokens:
            raise ValueError(f"Token {token.symbol} already exists")
        
        self.registered_tokens[token.symbol] = token
        print(f"Token {token.symbol} registered for {token.company_name}")
        
        return True
    
    def get_all_tokens(self) -> List[Dict]:
        """Get all registered tokens"""
        return [token.to_dict() for token in self.registered_tokens.values()]