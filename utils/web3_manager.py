"""
Web3 Integration Manager
Handles blockchain connections, wallet management, and contract interactions
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import streamlit as st
from typing import Dict, Optional, Tuple
import json
from decimal import Decimal

class Web3Manager:
    """Manages Web3 connections across multiple chains"""
    
    def __init__(self):
        self.connections = {}
        self.accounts = {}
        self.init_connections()
    
    def init_connections(self):
        """Initialize Web3 connections for all supported chains"""
        
        # Get RPC endpoints from secrets or use public ones
        rpc_config = self._get_rpc_config()
        
        for chain, config in rpc_config.items():
            try:
                w3 = Web3(Web3.HTTPProvider(
                    config['rpc'],
                    request_kwargs={'timeout': 60}
                ))
                
                # Add PoA middleware for BSC and Polygon
                if chain in ['bsc', 'polygon']:
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                if w3.is_connected():
                    self.connections[chain] = w3
                    st.success(f"✅ Connected to {chain.upper()}")
                else:
                    st.error(f"❌ Failed to connect to {chain.upper()}")
            except Exception as e:
                st.error(f"❌ Error connecting to {chain}: {str(e)}")
    
    def _get_rpc_config(self) -> Dict:
        """Get RPC configuration from secrets or use defaults"""
        
        # Try to get from Streamlit secrets first
        try:
            return {
                'bsc': {
                    'rpc': st.secrets.get("bsc_rpc", "https://bsc-dataseed1.binance.org"),
                    'chain_id': 56
                },
                'polygon': {
                    'rpc': st.secrets.get("polygon_rpc", "https://polygon-rpc.com"),
                    'chain_id': 137
                },
                'arbitrum': {
                    'rpc': st.secrets.get("arbitrum_rpc", "https://arb1.arbitrum.io/rpc"),
                    'chain_id': 42161
                },
                'base': {
                    'rpc': st.secrets.get("base_rpc", "https://mainnet.base.org"),
                    'chain_id': 8453
                }
            }
        except:
            # Fallback to public RPCs (slower and rate-limited)
            st.warning("⚠️ Using public RPCs. Consider using private nodes for better performance.")
            return {
                'bsc': {
                    'rpc': "https://bsc-dataseed1.binance.org",
                    'chain_id': 56
                },
                'polygon': {
                    'rpc': "https://polygon-rpc.com",
                    'chain_id': 137
                },
                'arbitrum': {
                    'rpc': "https://arb1.arbitrum.io/rpc",
                    'chain_id': 42161
                },
                'base': {
                    'rpc': "https://mainnet.base.org",
                    'chain_id': 8453
                }
            }
    
    def get_web3(self, chain: str) -> Optional[Web3]:
        """Get Web3 instance for specific chain"""
        return self.connections.get(chain)
    
    def load_account(self, private_key: str) -> Tuple[bool, str]:
        """Load wallet account from private key"""
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            
            account = Account.from_key(private_key)
            
            # Store account for all chains
            for chain in self.connections.keys():
                self.accounts[chain] = account
            
            return True, account.address
        except Exception as e:
            return False, f"Error loading account: {str(e)}"
    
    def get_balance(self, chain: str, address: str) -> Optional[float]:
        """Get native token balance"""
        try:
            w3 = self.get_web3(chain)
            if not w3:
                return None
            
            balance_wei = w3.eth.get_balance(address)
            balance = w3.from_wei(balance_wei, 'ether')
            return float(balance)
        except Exception as e:
            st.error(f"Error getting balance: {str(e)}")
            return None
    
    def get_token_balance(self, chain: str, token_address: str, wallet_address: str) -> Optional[float]:
        """Get ERC20 token balance"""
        try:
            w3 = self.get_web3(chain)
            if not w3:
                return None
            
            # ERC20 ABI for balanceOf
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]
            
            contract = w3.eth.contract(address=token_address, abi=erc20_abi)
            balance = contract.functions.balanceOf(wallet_address).call()
            decimals = contract.functions.decimals().call()
            
            return balance / (10 ** decimals)
        except Exception as e:
            st.error(f"Error getting token balance: {str(e)}")
            return None
    
    def estimate_gas(self, chain: str, transaction: Dict) -> Optional[int]:
        """Estimate gas for transaction"""
        try:
            w3 = self.get_web3(chain)
            if not w3:
                return None
            
            gas_estimate = w3.eth.estimate_gas(transaction)
            return gas_estimate
        except Exception as e:
            st.error(f"Error estimating gas: {str(e)}")
            return None
    
    def get_gas_price(self, chain: str, strategy: str = 'medium') -> Optional[int]:
        """
        Get optimized gas price based on strategy
        
        Args:
            chain: blockchain name
            strategy: 'slow', 'medium', 'fast', 'instant'
        """
        try:
            w3 = self.get_web3(chain)
            if not w3:
                return None
            
            # Get current gas price
            base_gas = w3.eth.gas_price
            
            # Apply strategy multiplier
            multipliers = {
                'slow': 0.8,      # 80% of current (might be slow)
                'medium': 1.0,    # Current price
                'fast': 1.2,      # 120% for faster confirmation
                'instant': 1.5    # 150% for immediate confirmation
            }
            
            multiplier = multipliers.get(strategy, 1.0)
            optimized_gas = int(base_gas * multiplier)
            
            return optimized_gas
        except Exception as e:
            st.error(f"Error getting gas price: {str(e)}")
            return None
    
    def check_allowance(self, chain: str, token_address: str, owner: str, spender: str) -> Optional[float]:
        """Check token allowance for spender"""
        try:
            w3 = self.get_web3(chain)
            if not w3:
                return None
            
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [
                        {"name": "_owner", "type": "address"},
                        {"name": "_spender", "type": "address"}
                    ],
                    "name": "allowance",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]
            
            contract = w3.eth.contract(address=token_address, abi=erc20_abi)
            allowance = contract.functions.allowance(owner, spender).call()
            decimals = contract.functions.decimals().call()
            
            return allowance / (10 ** decimals)
        except Exception as e:
            st.error(f"Error checking allowance: {str(e)}")
            return None
    
    def approve_token(self, chain: str, token_address: str, spender: str, amount: Optional[int] = None) -> Tuple[bool, str]:
        """
        Approve token spending
        
        Args:
            amount: Amount to approve. If None, approve max uint256
        """
        try:
            w3 = self.get_web3(chain)
            account = self.accounts.get(chain)
            
            if not w3 or not account:
                return False, "Web3 or account not initialized"
            
            # Max uint256 for unlimited approval
            if amount is None:
                amount = 2**256 - 1
            
            erc20_abi = [
                {
                    "constant": False,
                    "inputs": [
                        {"name": "_spender", "type": "address"},
                        {"name": "_value", "type": "uint256"}
                    ],
                    "name": "approve",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }
            ]
            
            contract = w3.eth.contract(address=token_address, abi=erc20_abi)
            
            # Build transaction
            nonce = w3.eth.get_transaction_count(account.address)
            gas_price = self.get_gas_price(chain, 'fast')
            
            transaction = contract.functions.approve(spender, amount).build_transaction({
                'from': account.address,
                'gas': 100000,
                'gasPrice': gas_price,
                'nonce': nonce
            })
            
            # Sign and send
            signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for receipt
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 1:
                return True, tx_hash.hex()
            else:
                return False, "Transaction failed"
                
        except Exception as e:
            return False, f"Error approving token: {str(e)}"
    
    def send_transaction(self, chain: str, transaction: Dict) -> Tuple[bool, str]:
        """Sign and send transaction"""
        try:
            w3 = self.get_web3(chain)
            account = self.accounts.get(chain)
            
            if not w3 or not account:
                return False, "Web3 or account not initialized"
            
            # Get nonce
            transaction['nonce'] = w3.eth.get_transaction_count(account.address)
            
            # Estimate gas if not provided
            if 'gas' not in transaction:
                transaction['gas'] = self.estimate_gas(chain, transaction)
            
            # Get gas price if not provided
            if 'gasPrice' not in transaction and 'maxFeePerGas' not in transaction:
                transaction['gasPrice'] = self.get_gas_price(chain, 'fast')
            
            # Sign transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
            
            # Send transaction
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return True, tx_hash.hex()
            
        except Exception as e:
            return False, f"Error sending transaction: {str(e)}"
    
    def wait_for_receipt(self, chain: str, tx_hash: str, timeout: int = 120) -> Optional[Dict]:
        """Wait for transaction receipt"""
        try:
            w3 = self.get_web3(chain)
            if not w3:
                return None
            
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return dict(receipt)
        except Exception as e:
            st.error(f"Error waiting for receipt: {str(e)}")
            return None
    
    def get_transaction_status(self, chain: str, tx_hash: str) -> Optional[str]:
        """Get transaction status"""
        try:
            w3 = self.get_web3(chain)
            if not w3:
                return None
            
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            
            if receipt:
                if receipt['status'] == 1:
                    return "success"
                else:
                    return "failed"
            else:
                return "pending"
        except:
            return "pending"
    
    def calculate_slippage_amount(self, amount: float, slippage_percent: float, is_min: bool = True) -> int:
        """
        Calculate amount with slippage protection
        
        Args:
            amount: Original amount
            slippage_percent: Slippage tolerance (e.g., 0.5 for 0.5%)
            is_min: True for minimum output, False for maximum input
        """
        slippage_multiplier = 1 - (slippage_percent / 100) if is_min else 1 + (slippage_percent / 100)
        return int(amount * slippage_multiplier)
    
    def get_block_number(self, chain: str) -> Optional[int]:
        """Get current block number"""
        try:
            w3 = self.get_web3(chain)
            if not w3:
                return None
            return w3.eth.block_number
        except Exception as e:
            st.error(f"Error getting block number: {str(e)}")
            return None
    
    def is_contract(self, chain: str, address: str) -> bool:
        """Check if address is a contract"""
        try:
            w3 = self.get_web3(chain)
            if not w3:
                return False
            
            code = w3.eth.get_code(address)
            return len(code) > 0
        except:
            return False
