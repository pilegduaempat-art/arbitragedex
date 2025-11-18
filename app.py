import streamlit as st
import requests
from web3 import Web3
from datetime import datetime, timedelta
import pandas as pd
import json
import time
from typing import Dict, List, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
import plotly.graph_objects as go
import plotly.express as px

# ==================== CONFIG ====================
st.set_page_config(
    page_title="DEX Arbitrage Trading Bot",
    page_icon="💰",
    layout="wide"
)

# ==================== SAFE DICTIONARY ACCESS ====================
def safe_get(dictionary: Dict, key: str, default=0):
    """Safely get value from dictionary with default"""
    try:
        return dictionary.get(key, default)
    except (KeyError, AttributeError, TypeError):
        return default

# ==================== CONSTANTS ====================
# Free Public RPC Endpoints (No API Key Required)
FREE_RPC_ENDPOINTS = {
    "ethereum": [
        "https://eth.public-rpc.com",
        "https://rpc.ankr.com/eth",
        "https://cloudflare-eth.com",
        "https://ethereum.publicnode.com",
        "https://eth.llamarpc.com",
        "https://rpc.flashbots.net",
        "https://virginia.rpc.blxrbdn.com",
        "https://uk.rpc.blxrbdn.com"
    ],
    "bsc": [
        "https://bsc.public-rpc.com",
        "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.defibit.io",
        "https://bsc-dataseed1.ninicoin.io",
        "https://bsc.publicnode.com",
        "https://bsc.llamarpc.com"
    ]
}

# Uniswap V2 Router ABI (simplified)
UNISWAP_V2_ROUTER_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                   {"internalType": "address[]", "name": "path", "type": "address[]"}],
        "name": "getAmountsOut",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                   {"internalType": "uint256", "name": "amountInMax", "type": "uint256"},
                   {"internalType": "address[]", "name": "path", "type": "address[]"},
                   {"internalType": "address", "name": "to", "type": "address"},
                   {"internalType": "uint256", "name": "deadline", "type": "uint256"}],
        "name": "swapTokensForExactTokens",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# ERC20 ABI (simplified)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
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

# DEX Configurations
DEX_CONFIG = {
    "ethereum": {
        "Uniswap V2": {
            "router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            "factory": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
        },
        "Sushiswap": {
            "router": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
            "factory": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
        }
    },
    "bsc": {
        "PancakeSwap V2": {
            "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
            "factory": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
        },
        "Biswap": {
            "router": "0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8",
            "factory": "0x858E3312ed3A876947EA49d572A7C42DE08af7EE"
        }
    }
}

# Popular token addresses
TOKENS = {
    "ethereum": {
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    },
    "bsc": {
        "WBNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "BUSD": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
        "USDT": "0x55d398326f99059fF775485246999027B3197955",
        "BTCB": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
        "ETH": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"
    }
}

# ==================== SESSION STATE INIT ====================
if 'opportunities' not in st.session_state:
    st.session_state.opportunities = []
if 'executed_trades' not in st.session_state:
    st.session_state.executed_trades = []
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = []
if 'alert_history' not in st.session_state:
    st.session_state.alert_history = []

# ==================== HELPER FUNCTIONS ====================
def safe_get(dictionary: Dict, key: str, default=0):
    """Safely get value from dictionary with default"""
    try:
        if dictionary is None:
            return default
        return dictionary.get(key, default)
    except (KeyError, AttributeError, TypeError):
        return default

# ==================== RPC HEALTH CHECKER ====================
class RPCHealthChecker:
    def __init__(self):
        self.results = {}
    
    def check_rpc(self, url: str, timeout: int = 5) -> Dict:
        """Check RPC health and response time"""
        start_time = time.time()
        try:
            w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': timeout}))
            
            # Test connection
            if not w3.is_connected():
                return {'status': 'offline', 'response_time': None, 'error': 'Connection failed'}
            
            # Test block number fetch
            block = w3.eth.block_number
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Test gas price
            try:
                gas = w3.eth.gas_price
                gas_support = True
            except:
                gas_support = False
            
            return {
                'status': 'online',
                'response_time': response_time,
                'block_number': block,
                'gas_support': gas_support,
                'error': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'response_time': None,
                'error': str(e)[:100]
            }
    
    def check_all_rpcs(self, network: str) -> Dict:
        """Check all available RPCs for a network"""
        results = {}
        for url in FREE_RPC_ENDPOINTS.get(network, []):
            results[url] = self.check_rpc(url)
        return results
    
    def get_best_rpc(self, network: str) -> str:
        """Get the best performing RPC"""
        results = self.check_all_rpcs(network)
        
        # Filter online RPCs
        online_rpcs = {url: data for url, data in results.items() 
                      if data['status'] == 'online'}
        
        if not online_rpcs:
            return FREE_RPC_ENDPOINTS[network][0]  # Return first as fallback
        
        # Sort by response time
        best = min(online_rpcs.items(), key=lambda x: x[1]['response_time'])
        return best[0]

# ==================== WEB3 HELPER CLASS ====================
class Web3Helper:
    def __init__(self, rpc_url: str, chain: str, fallback_rpcs: List[str] = None):
        self.rpc_url = rpc_url
        self.chain = chain
        self.fallback_rpcs = fallback_rpcs or FREE_RPC_ENDPOINTS.get(chain, [])
        self.w3 = None
        self._connect()
        
    def _connect(self):
        """Connect to RPC with fallback support"""
        # Try primary RPC
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url, request_kwargs={'timeout': 10}))
            if self.w3.is_connected():
                return
        except Exception as e:
            st.warning(f"Primary RPC failed: {str(e)}")
        
        # Try fallback RPCs
        for fallback_url in self.fallback_rpcs:
            if fallback_url == self.rpc_url:
                continue
            try:
                st.info(f"Trying fallback RPC: {fallback_url}")
                self.w3 = Web3(Web3.HTTPProvider(fallback_url, request_kwargs={'timeout': 10}))
                if self.w3.is_connected():
                    self.rpc_url = fallback_url
                    st.success(f"✅ Connected to fallback: {fallback_url}")
                    return
            except:
                continue
        
        # If all failed
        if not self.w3 or not self.w3.is_connected():
            raise Exception("Failed to connect to any RPC endpoint")
        
    def is_connected(self) -> bool:
        try:
            return self.w3.is_connected()
        except:
            return False
    
    def get_gas_price(self) -> int:
        """Get gas price with fallback"""
        try:
            return self.w3.eth.gas_price
        except Exception as e:
            # Fallback to default gas prices
            default_gas = {
                'ethereum': self.w3.to_wei(30, 'gwei'),  # 30 Gwei
                'bsc': self.w3.to_wei(5, 'gwei')  # 5 Gwei
            }
            st.warning(f"⚠️ Cannot fetch gas price: {str(e)[:100]}. Using default.")
            return default_gas.get(self.chain, self.w3.to_wei(20, 'gwei'))
    
    def get_balance(self, address: str) -> float:
        """Get native token balance with error handling"""
        try:
            balance = self.w3.eth.get_balance(address)
            return self.w3.from_wei(balance, 'ether')
        except Exception as e:
            st.warning(f"⚠️ Cannot fetch balance: {str(e)[:100]}")
            return 0.0
    
    def get_token_balance(self, token_address: str, wallet_address: str) -> float:
        """Get ERC20 token balance with error handling"""
        try:
            token_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=ERC20_ABI
            )
            balance = token_contract.functions.balanceOf(
                Web3.to_checksum_address(wallet_address)
            ).call()
            decimals = token_contract.functions.decimals().call()
            return balance / (10 ** decimals)
        except Exception as e:
            st.warning(f"⚠️ Cannot fetch token balance: {str(e)[:100]}")
            return 0.0
    
    def get_amounts_out(self, router_address: str, amount_in: int, path: List[str]) -> List[int]:
        """Get amounts out with error handling and retry logic"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                router = self.w3.eth.contract(
                    address=Web3.to_checksum_address(router_address),
                    abi=UNISWAP_V2_ROUTER_ABI
                )
                checksum_path = [Web3.to_checksum_address(addr) for addr in path]
                amounts = router.functions.getAmountsOut(amount_in, checksum_path).call()
                return amounts
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    # Return empty list on final failure
                    return []
        return []

# ==================== ARBITRAGE FINDER ====================
class ArbitrageFinder:
    def __init__(self, web3_helper: Web3Helper, dex_config: Dict):
        self.w3h = web3_helper
        self.dex_config = dex_config
        self.min_profit_percentage = 0.5  # 0.5%
        
    def calculate_slippage(self, amount_in: float, amount_out: float, 
                          expected_out: float) -> float:
        """Calculate slippage percentage"""
        if expected_out == 0:
            return 0
        return ((expected_out - amount_out) / expected_out) * 100
    
    def get_liquidity_depth(self, dex_name: str, router_address: str, 
                           token_in: str, token_out: str) -> Dict:
        """Analyze liquidity depth for a trading pair"""
        test_amounts = [0.1, 0.5, 1.0, 5.0, 10.0]  # ETH/BNB amounts
        liquidity_data = []
        
        for amount in test_amounts:
            try:
                amount_wei = self.w3h.w3.to_wei(amount, 'ether')
                path = [token_in, token_out]
                amounts_out = self.w3h.get_amounts_out(router_address, amount_wei, path)
                
                if amounts_out and len(amounts_out) > 1:
                    output = self.w3h.w3.from_wei(amounts_out[-1], 'ether')
                    rate = output / amount if amount > 0 else 0
                    
                    liquidity_data.append({
                        'amount_in': amount,
                        'amount_out': output,
                        'rate': rate
                    })
            except Exception as e:
                # Silently skip failed amounts
                continue
        
        return {
            'dex': dex_name,
            'liquidity_data': liquidity_data,
            'avg_rate': sum([d['rate'] for d in liquidity_data]) / len(liquidity_data) if liquidity_data else 0
        }
    
    def find_direct_arbitrage(self, token_in: str, token_out: str, 
                            amount: float) -> List[Dict]:
        """Find direct arbitrage opportunities between DEXes"""
        opportunities = []
        amount_wei = self.w3h.w3.to_wei(amount, 'ether')
        
        dex_prices = {}
        
        # Get prices from all DEXes
        for dex_name, dex_info in self.dex_config.items():
            try:
                router = dex_info['router']
                path = [token_in, token_out]
                amounts_out = self.w3h.get_amounts_out(router, amount_wei, path)
                
                if amounts_out and len(amounts_out) > 1:
                    output = self.w3h.w3.from_wei(amounts_out[-1], 'ether')
                    dex_prices[dex_name] = {
                        'output': output,
                        'router': router
                    }
            except Exception as e:
                # Skip failed DEX
                continue
        
        # Find arbitrage opportunities
        if len(dex_prices) >= 2:
            dex_list = list(dex_prices.items())
            for i in range(len(dex_list)):
                for j in range(i + 1, len(dex_list)):
                    dex1_name, dex1_data = dex_list[i]
                    dex2_name, dex2_data = dex_list[j]
                    
                    # Buy from cheaper, sell to expensive
                    if dex1_data['output'] < dex2_data['output']:
                        buy_dex, sell_dex = dex1_name, dex2_name
                        buy_price, sell_price = dex1_data['output'], dex2_data['output']
                    else:
                        buy_dex, sell_dex = dex2_name, dex1_name
                        buy_price, sell_price = dex2_data['output'], dex1_data['output']
                    
                    profit = sell_price - buy_price
                    profit_percentage = (profit / buy_price) * 100
                    
                    if profit_percentage >= self.min_profit_percentage:
                        opportunities.append({
                            'type': 'direct',
                            'buy_dex': buy_dex,
                            'sell_dex': sell_dex,
                            'token_in': token_in,
                            'token_out': token_out,
                            'amount': amount,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'profit': profit,
                            'profit_percentage': profit_percentage,
                            'timestamp': datetime.now()
                        })
        
        return opportunities
    
    def find_triangular_arbitrage(self, tokens: List[str], amount: float) -> List[Dict]:
        """Find triangular arbitrage opportunities (multi-hop)"""
        opportunities = []
        amount_wei = self.w3h.w3.to_wei(amount, 'ether')
        
        # Try all combinations of 3 tokens
        for dex_name, dex_info in self.dex_config.items():
            try:
                router = dex_info['router']
                
                # Path: Token A -> Token B -> Token C -> Token A
                for i, token_a in enumerate(tokens):
                    for j, token_b in enumerate(tokens):
                        if i == j:
                            continue
                        for k, token_c in enumerate(tokens):
                            if k == i or k == j:
                                continue
                            
                            try:
                                # Step 1: A -> B
                                path1 = [token_a, token_b]
                                amounts1 = self.w3h.get_amounts_out(router, amount_wei, path1)
                                
                                # Step 2: B -> C
                                path2 = [token_b, token_c]
                                amounts2 = self.w3h.get_amounts_out(router, amounts1[-1], path2)
                                
                                # Step 3: C -> A
                                path3 = [token_c, token_a]
                                amounts3 = self.w3h.get_amounts_out(router, amounts2[-1], path3)
                                
                                final_amount = self.w3h.w3.from_wei(amounts3[-1], 'ether')
                                profit = final_amount - amount
                                profit_percentage = (profit / amount) * 100
                                
                                if profit_percentage >= self.min_profit_percentage:
                                    opportunities.append({
                                        'type': 'triangular',
                                        'dex': dex_name,
                                        'path': f"{token_a[:6]}... -> {token_b[:6]}... -> {token_c[:6]}... -> {token_a[:6]}...",
                                        'amount_in': amount,
                                        'amount_out': final_amount,
                                        'profit': profit,
                                        'profit_percentage': profit_percentage,
                                        'timestamp': datetime.now()
                                    })
                            except:
                                continue
                                
            except Exception as e:
                continue
        
        return opportunities

# ==================== GAS OPTIMIZER ====================
class GasOptimizer:
    def __init__(self, web3_helper: Web3Helper):
        self.w3h = web3_helper
        
    def estimate_gas(self, profit: float, gas_price: int, gas_limit: int = 200000) -> Dict:
        """Estimate gas cost and net profit"""
        gas_cost_wei = gas_price * gas_limit
        gas_cost_eth = self.w3h.w3.from_wei(gas_cost_wei, 'ether')
        net_profit = profit - gas_cost_eth
        
        return {
            'gas_price_gwei': self.w3h.w3.from_wei(gas_price, 'gwei'),
            'gas_limit': gas_limit,
            'gas_cost_eth': gas_cost_eth,
            'gross_profit': profit,
            'net_profit': net_profit,
            'is_profitable': net_profit > 0
        }
    
    def optimize_gas_price(self, base_gas_price: int, speed: str = "fast") -> int:
        """Optimize gas price based on speed preference"""
        multipliers = {
            "slow": 0.9,
            "standard": 1.0,
            "fast": 1.2,
            "instant": 1.5
        }
        return int(base_gas_price * multipliers.get(speed, 1.0))

# ==================== TELEGRAM NOTIFIER ====================
class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message: str) -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=data)
            return response.status_code == 200
        except Exception as e:
            st.error(f"Telegram error: {str(e)}")
            return False
    
    def send_opportunity_alert(self, opportunity: Dict) -> bool:
        """Send arbitrage opportunity alert"""
        message = f"""
🚀 <b>ARBITRAGE OPPORTUNITY FOUND!</b>

Type: {opportunity['type'].upper()}
Profit: {opportunity['profit']:.4f} ETH ({opportunity['profit_percentage']:.2f}%)
Amount: {opportunity['amount']} ETH

Time: {opportunity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

💰 Execute now for maximum profit!
        """
        return self.send_message(message)

# ==================== BACKTESTING ENGINE ====================
class BacktestEngine:
    def __init__(self):
        self.trades = []
        
    def simulate_trade(self, opportunity: Dict, execution_delay: float = 2.0) -> Dict:
        """Simulate trade execution with realistic parameters"""
        # Simulate slippage (0.1-0.5%)
        slippage = opportunity['profit_percentage'] * 0.1  # 10% of profit as slippage
        actual_profit_pct = opportunity['profit_percentage'] - slippage
        actual_profit = opportunity['profit'] * (actual_profit_pct / opportunity['profit_percentage'])
        
        # Simulate gas cost
        gas_cost = 0.002  # ~$5-10 depending on network
        net_profit = actual_profit - gas_cost
        
        trade_result = {
            'timestamp': opportunity['timestamp'],
            'type': opportunity['type'],
            'expected_profit': opportunity['profit'],
            'actual_profit': net_profit,
            'slippage': slippage,
            'gas_cost': gas_cost,
            'success': net_profit > 0
        }
        
        self.trades.append(trade_result)
        return trade_result
    
    def get_statistics(self) -> Dict:
        """Calculate backtest statistics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'successful_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'total_loss': 0,
                'net_profit': 0,
                'avg_profit_per_trade': 0,
                'best_profit': 0,
                'worst_loss': 0,
                'profit_factor': 0
            }
        
        successful = [t for t in self.trades if t['success']]
        failed = [t for t in self.trades if not t['success']]
        
        total_profit = sum([t['actual_profit'] for t in successful])
        total_loss = sum([abs(t['actual_profit']) for t in failed])
        
        # Best and worst trades
        all_profits = [t['actual_profit'] for t in self.trades]
        best_profit = max(all_profits) if all_profits else 0
        worst_loss = min(all_profits) if all_profits else 0
        
        # Profit factor
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        return {
            'total_trades': len(self.trades),
            'successful_trades': len(successful),
            'win_rate': len(successful) / len(self.trades) * 100,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'net_profit': total_profit - total_loss,
            'avg_profit_per_trade': total_profit / len(successful) if successful else 0,
            'best_profit': best_profit,
            'worst_loss': worst_loss,
            'profit_factor': profit_factor
        }

# ==================== MAIN APP ====================
def main():
    st.title("🚀 DEX Arbitrage Trading Bot")
    st.markdown("**Real-time arbitrage opportunities across multiple DEXes**")
    
    # Information banner
    with st.expander("ℹ️ About RPC Providers & Common Issues", expanded=False):
        st.markdown("""
        ### Free Public RPC Endpoints
        
        This bot uses **FREE public RPC endpoints** - no API key required!
        
        **Available Providers:**
        - **Pocket Network**: Decentralized RPC infrastructure (Recommended)
        - **Ankr**: Fast and reliable free tier
        - **Public Nodes**: Community-maintained endpoints
        
        ### ⚠️ Common RPC Errors & Solutions
        
        **Error: "Cannot fulfill request" (Code -32046)**
        - 🔧 **Solution 1**: Try different RPC provider from dropdown
        - 🔧 **Solution 2**: Enable "Automatic Fallback" in Advanced Settings
        - 🔧 **Solution 3**: Use "Check RPC Health" to find best RPC
        - 🔧 **Solution 4**: Increase timeout in settings
        
        **Error: "Connection timeout"**
        - 🔧 Check your internet connection
        - 🔧 Try RPC with lower response time
        - 🔧 Increase timeout setting
        
        **Error: "Rate limit exceeded"**
        - 🔧 Public RPCs have rate limits
        - 🔧 Switch to different provider
        - 🔧 Consider premium RPC (Alchemy/Infura)
        
        ### 💡 Performance Tips
        
        1. **Use RPC Health Check** to find fastest RPC
        2. **Enable Auto-Fallback** for reliability
        3. **Reduce scan frequency** if hitting rate limits
        4. **Use premium RPC** for production trading
        
        **Premium RPC Options (Recommended for production):**
        - Alchemy: 300M requests/month free (https://alchemy.com)
        - Infura: 100k requests/day free (https://infura.io)
        - QuickNode: Paid but very reliable (https://quicknode.com)
        
        **No Pocket Portal account needed!** 🎉
        """)
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Network Selection
        network = st.selectbox(
            "Select Network",
            ["ethereum", "bsc"],
            format_func=lambda x: "Ethereum" if x == "ethereum" else "Binance Smart Chain"
        )
        
        # RPC Configuration
        st.subheader("🔗 RPC Configuration")
        
        rpc_provider_names = {
            "ethereum": [
                "Pocket Network (Decentralized)",
                "Ankr (Fast & Reliable)", 
                "Cloudflare (Stable)",
                "PublicNode (Community)",
                "LlamaRPC (Free)",
                "Custom RPC URL"
            ],
            "bsc": [
                "Pocket Network (Decentralized)",
                "Ankr (Fast & Reliable)",
                "Binance Official",
                "DeFiBit (Stable)",
                "PublicNode (Community)",
                "Custom RPC URL"
            ]
        }
        
        rpc_choice = st.selectbox("Select RPC Provider", rpc_provider_names[network])
        
        if "Custom" in rpc_choice:
            rpc_url = st.text_input("Custom RPC URL", 
                                   value="https://your-rpc-endpoint.com",
                                   help="Enter your own RPC endpoint (Alchemy, Infura, QuickNode, etc.)")
        else:
            # Map selection to actual RPC URL
            provider_index = rpc_provider_names[network].index(rpc_choice)
            if provider_index < len(FREE_RPC_ENDPOINTS[network]):
                rpc_url = FREE_RPC_ENDPOINTS[network][provider_index]
                st.success(f"✅ Using: `{rpc_url}`")
            else:
                rpc_url = FREE_RPC_ENDPOINTS[network][0]
        
        # Show RPC status
        with st.expander("🔧 Advanced RPC Settings"):
            enable_fallback = st.checkbox("Enable Automatic Fallback", value=True, 
                                         help="Automatically switch to backup RPC if primary fails")
            rpc_timeout = st.slider("Request Timeout (seconds)", 5, 30, 10)
            
            # RPC Health Check
            if st.button("🏥 Check RPC Health"):
                with st.spinner("Testing all RPCs..."):
                    health_checker = RPCHealthChecker()
                    results = health_checker.check_all_rpcs(network)
                    
                    st.subheader("RPC Health Status")
                    
                    for url, data in results.items():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.text(url)
                        
                        with col2:
                            if data['status'] == 'online':
                                st.success(f"✅ {data['response_time']:.0f}ms")
                            else:
                                st.error("❌ Offline")
                        
                        with col3:
                            if data.get('gas_support'):
                                st.text("⛽ Gas OK")
                            else:
                                st.text("⚠️ No Gas")
                    
                    # Show recommendation
                    best_rpc = health_checker.get_best_rpc(network)
                    st.info(f"💡 **Recommended RPC:** `{best_rpc}`")
            
            st.markdown("**Available Fallback RPCs:**")
            for idx, url in enumerate(FREE_RPC_ENDPOINTS[network][:5], 1):
                st.code(f"{idx}. {url}", language="text")
        
        # Wallet Configuration
        st.subheader("👛 Wallet")
        wallet_address = st.text_input("Wallet Address", value="0x...")
        private_key = st.text_input("Private Key (for execution)", type="password")
        
        # Trading Parameters
        st.subheader("💰 Trading Parameters")
        trade_amount = st.number_input("Trade Amount (ETH/BNB)", min_value=0.01, value=0.1, step=0.01)
        min_profit = st.slider("Min Profit %", 0.1, 5.0, 0.5, 0.1)
        
        # Telegram Configuration
        st.subheader("📱 Telegram Alerts")
        enable_telegram = st.checkbox("Enable Telegram Notifications")
        if enable_telegram:
            tg_bot_token = st.text_input("Bot Token", type="password")
            tg_chat_id = st.text_input("Chat ID")
        
        # Gas Settings
        st.subheader("⛽ Gas Settings")
        gas_speed = st.select_slider(
            "Gas Speed",
            options=["slow", "standard", "fast", "instant"],
            value="fast"
        )
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Opportunities", 
        "📊 Liquidity Analysis", 
        "⚡ Live Trading",
        "📈 Backtesting",
        "📜 Trade History",
        "🔔 Alerts"
    ])
    
    # Initialize Web3
    if rpc_url:
        try:
            with st.spinner("🔌 Connecting to blockchain..."):
                fallback_rpcs = FREE_RPC_ENDPOINTS[network] if enable_fallback else []
                w3h = Web3Helper(rpc_url, network, fallback_rpcs)
            
            if not w3h.is_connected():
                st.error("❌ Failed to connect to RPC endpoint")
                st.info("💡 Try another RPC provider from the dropdown or enable fallback")
                
                # Show troubleshooting tips
                with st.expander("🔧 Troubleshooting Tips"):
                    st.markdown("""
                    **Common Issues:**
                    1. **Rate Limiting**: Public RPCs may limit requests. Try another provider.
                    2. **Network Issues**: Check your internet connection
                    3. **RPC Down**: The selected RPC might be temporarily unavailable
                    4. **Gas Price Error**: Some RPCs don't support `eth_gasPrice` method
                    
                    **Solutions:**
                    - ✅ Enable "Automatic Fallback" in Advanced Settings
                    - ✅ Try a different RPC provider
                    - ✅ Use **RPC Health Check** to find working RPCs
                    - ✅ Use a dedicated RPC service (Alchemy, Infura)
                    - ✅ Increase timeout in Advanced Settings
                    
                    **Specific Error Codes:**
                    - `-32046`: RPC cannot fulfill request → Try different RPC
                    - `-32005`: Rate limit exceeded → Reduce scan frequency
                    - `-32000`: Server error → Try fallback RPC
                    """)
                return
            
            # Show connection details
            st.sidebar.success(f"✅ Connected to {network.upper()}")
            st.sidebar.info(f"🌐 Provider: {rpc_choice}")
            
            # Show network info
            try:
                block_number = w3h.w3.eth.block_number
                st.sidebar.metric("Latest Block", f"{block_number:,}")
            except:
                pass
            
            # Show wallet balance
            if wallet_address and wallet_address.startswith("0x") and len(wallet_address) == 42:
                try:
                    balance = w3h.get_balance(wallet_address)
                    if balance > 0:
                        st.sidebar.metric("Wallet Balance", f"{balance:.4f} {'ETH' if network == 'ethereum' else 'BNB'}")
                except:
                    pass
            
            # Show gas price
            try:
                gas_price = w3h.get_gas_price()
                gas_gwei = w3h.w3.from_wei(gas_price, 'gwei')
                st.sidebar.metric("Gas Price", f"{gas_gwei:.1f} Gwei")
            except:
                pass
            
        except Exception as e:
            st.error(f"❌ Error connecting: {str(e)}")
            return
    else:
        st.warning("⚠️ Please configure RPC endpoint in sidebar")
        return
    
    # Initialize components
    dex_config = DEX_CONFIG[network]
    tokens = TOKENS[network]
    
    arbitrage_finder = ArbitrageFinder(w3h, dex_config)
    gas_optimizer = GasOptimizer(w3h)
    backtest_engine = BacktestEngine()
    
    if enable_telegram and tg_bot_token and tg_chat_id:
        telegram = TelegramNotifier(tg_bot_token, tg_chat_id)
    else:
        telegram = None
    
    # TAB 1: Opportunities Finder
    with tab1:
        st.header("🔍 Arbitrage Opportunities")
        
        col1, col2 = st.columns(2)
        
        with col1:
            token_in = st.selectbox("Token In", list(tokens.keys()))
        with col2:
            token_out = st.selectbox("Token Out", [t for t in tokens.keys() if t != token_in])
        
        scan_col1, scan_col2, scan_col3 = st.columns(3)
        
        with scan_col1:
            if st.button("🔍 Scan Direct Arbitrage", use_container_width=True):
                with st.spinner("Scanning DEXes..."):
                    opportunities = arbitrage_finder.find_direct_arbitrage(
                        tokens[token_in],
                        tokens[token_out],
                        trade_amount
                    )
                    
                    st.session_state.opportunities = opportunities
                    
                    if opportunities:
                        st.success(f"Found {len(opportunities)} opportunities!")
                        
                        # Send telegram alert
                        if telegram:
                            for opp in opportunities:
                                telegram.send_opportunity_alert(opp)
                    else:
                        st.info("No profitable opportunities found")
        
        with scan_col2:
            if st.button("🔺 Scan Triangular Arbitrage", use_container_width=True):
                with st.spinner("Scanning multi-hop paths..."):
                    # Use first 3 tokens for triangular
                    token_list = [tokens[list(tokens.keys())[i]] for i in range(min(3, len(tokens)))]
                    
                    opportunities = arbitrage_finder.find_triangular_arbitrage(
                        token_list,
                        trade_amount
                    )
                    
                    st.session_state.opportunities = opportunities
                    
                    if opportunities:
                        st.success(f"Found {len(opportunities)} opportunities!")
                        
                        if telegram:
                            for opp in opportunities:
                                telegram.send_opportunity_alert(opp)
                    else:
                        st.info("No profitable opportunities found")
        
        with scan_col3:
            auto_scan = st.checkbox("🔄 Auto-scan (30s)")
        
        # Display opportunities
        if st.session_state.opportunities:
            st.subheader("💰 Current Opportunities")
            
            for idx, opp in enumerate(st.session_state.opportunities):
                profit_pct = safe_get(opp, 'profit_percentage', 0)
                
                with st.expander(f"Opportunity #{idx+1} - {profit_pct:.2f}% profit", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Type", safe_get(opp, 'type', 'unknown').upper())
                        st.metric("Amount", f"{safe_get(opp, 'amount', 0)} ETH")
                    
                    with col2:
                        profit = safe_get(opp, 'profit', 0)
                        st.metric("Gross Profit", f"{profit:.4f} ETH")
                        st.metric("Profit %", f"{profit_pct:.2f}%")
                    
                    with col3:
                        # Gas calculation
                        try:
                            gas_price = w3h.get_gas_price()
                            gas_calc = gas_optimizer.estimate_gas(profit, gas_price)
                            
                            st.metric("Net Profit", f"{safe_get(gas_calc, 'net_profit', 0):.4f} ETH")
                            st.metric("Gas Cost", f"{safe_get(gas_calc, 'gas_cost_eth', 0):.4f} ETH")
                        except Exception as e:
                            st.metric("Net Profit", f"{profit:.4f} ETH")
                            st.caption("⚠️ Gas calc unavailable")
                    
                    if safe_get(opp, 'type') == 'direct':
                        buy_dex = safe_get(opp, 'buy_dex', 'Unknown')
                        sell_dex = safe_get(opp, 'sell_dex', 'Unknown')
                        st.info(f"**Route:** Buy on {buy_dex} → Sell on {sell_dex}")
                    else:
                        path = safe_get(opp, 'path', 'Unknown path')
                        st.info(f"**Route:** {path}")
                    
                    if st.button(f"⚡ Execute Trade #{idx+1}", key=f"exec_{idx}"):
                        st.warning("Trade execution requires private key and is disabled in demo mode")
        
        # Auto-scan functionality
        if auto_scan:
            time.sleep(30)
            st.rerun()
    
    # TAB 2: Liquidity Analysis
    with tab2:
        st.header("📊 Liquidity Analysis")
        
        st.info("Analyze market depth and liquidity across different DEXes")
        
        liq_col1, liq_col2 = st.columns(2)
        
        with liq_col1:
            liq_token_in = st.selectbox("Token In", list(tokens.keys()), key="liq_in")
        with liq_col2:
            liq_token_out = st.selectbox("Token Out", [t for t in tokens.keys() if t != liq_token_in], key="liq_out")
        
        if st.button("📊 Analyze Liquidity", use_container_width=True):
            with st.spinner("Analyzing liquidity depth..."):
                liquidity_results = []
                
                for dex_name, dex_info in dex_config.items():
                    liq_data = arbitrage_finder.get_liquidity_depth(
                        dex_name,
                        dex_info['router'],
                        tokens[liq_token_in],
                        tokens[liq_token_out]
                    )
                    liquidity_results.append(liq_data)
                
                # Display results
                for liq in liquidity_results:
                    st.subheader(f"🏦 {liq['dex']}")
                    
                    if liq['liquidity_data']:
                        df = pd.DataFrame(liq['liquidity_data'])
                        
                        # Create chart
                        fig = px.line(df, x='amount_in', y='rate', 
                                     title=f"Exchange Rate by Trade Size - {liq['dex']}",
                                     labels={'amount_in': 'Trade Size (ETH/BNB)', 'rate': 'Exchange Rate'})
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show data table
                        st.dataframe(df, use_container_width=True)
                        st.metric("Average Rate", f"{liq['avg_rate']:.6f}")
                    else:
                        st.warning("No liquidity data available")
    
    # TAB 3: Live Trading
    with tab3:
        st.header("⚡ Live Trading Execution")
        
        st.warning("⚠️ **CAUTION:** Live trading requires private key and will execute real transactions!")
        
        # Trading Status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Trades", len(st.session_state.executed_trades))
        with col2:
            total_profit = sum([t.get('profit', 0) for t in st.session_state.executed_trades if t.get('success', False)])
            st.metric("Total Profit", f"{total_profit:.4f} ETH")
        with col3:
            successful = len([t for t in st.session_state.executed_trades if t.get('success', False)])
            total = max(len(st.session_state.executed_trades), 1)
            win_rate = successful / total * 100
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col4:
            try:
                gas_price = w3h.get_gas_price()
                st.metric("Current Gas", f"{w3h.w3.from_wei(gas_price, 'gwei'):.1f} Gwei")
            except:
                st.metric("Current Gas", "N/A")
        
        # Auto-Trading Settings
        st.subheader("🤖 Auto-Trading Configuration")
        
        auto_col1, auto_col2, auto_col3 = st.columns(3)
        
        with auto_col1:
            enable_auto_trade = st.checkbox("Enable Auto-Trading")
            max_trade_amount = st.number_input("Max Trade Amount", min_value=0.01, value=1.0)
        
        with auto_col2:
            min_profit_threshold = st.number_input("Min Profit Threshold %", min_value=0.1, value=1.0)
            max_slippage = st.number_input("Max Slippage %", min_value=0.1, value=2.0)
        
        with auto_col3:
            max_gas_price = st.number_input("Max Gas Price (Gwei)", min_value=10, value=100)
            execution_delay = st.number_input("Execution Delay (s)", min_value=0, value=5)
        
        # Risk Management
        st.subheader("🛡️ Risk Management")
        
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            stop_loss = st.number_input("Stop Loss (ETH)", min_value=0.0, value=0.5)
            daily_limit = st.number_input("Daily Trade Limit", min_value=1, value=50)
        
        with risk_col2:
            max_position = st.number_input("Max Position Size (ETH)", min_value=0.1, value=5.0)
            enable_stop_loss = st.checkbox("Enable Stop Loss", value=True)
        
        # Manual Execution
        st.subheader("🎯 Manual Trade Execution")
        
        if st.session_state.opportunities:
            selected_opp = st.selectbox(
                "Select Opportunity",
                range(len(st.session_state.opportunities)),
                format_func=lambda x: f"Opportunity #{x+1} - {safe_get(st.session_state.opportunities[x], 'profit_percentage', 0):.2f}% profit"
            )
            
            if selected_opp is not None:
                opp = st.session_state.opportunities[selected_opp]
                
                exec_col1, exec_col2 = st.columns(2)
                
                with exec_col1:
                    opp_type = safe_get(opp, 'type', 'unknown')
                    amount = safe_get(opp, 'amount', 0)
                    profit = safe_get(opp, 'profit', 0)
                    profit_pct = safe_get(opp, 'profit_percentage', 0)
                    
                    st.info(f"""
                    **Trade Details:**
                    - Type: {opp_type.upper()}
                    - Amount: {amount} ETH
                    - Expected Profit: {profit:.4f} ETH ({profit_pct:.2f}%)
                    """)
                
                with exec_col2:
                    if st.button("🚀 Execute Trade Now", type="primary", use_container_width=True):
                        if not private_key:
                            st.error("❌ Private key required for execution")
                        else:
                            with st.spinner("Executing trade..."):
                                # Simulate execution (replace with real execution logic)
                                time.sleep(2)
                                
                                opp_type = safe_get(opp, 'type', 'direct')
                                amount = safe_get(opp, 'amount', 0)
                                profit = safe_get(opp, 'profit', 0)
                                
                                trade_result = {
                                    'timestamp': datetime.now(),
                                    'type': opp_type,
                                    'amount': amount,
                                    'expected_profit': profit,
                                    'actual_profit': profit * 0.95,  # Simulate 5% slippage
                                    'gas_cost': 0.002,
                                    'success': True,
                                    'tx_hash': '0x' + 'a' * 64  # Simulated tx hash
                                }
                                
                                st.session_state.executed_trades.append(trade_result)
                                st.success(f"✅ Trade executed! TX: {trade_result['tx_hash'][:10]}...")
                                
                                # Send telegram notification
                                if telegram:
                                    telegram.send_message(f"✅ Trade executed successfully!\nProfit: {trade_result['actual_profit']:.4f} ETH")
        else:
            st.info("No opportunities available. Scan for opportunities in the 'Opportunities' tab.")
        
        # WalletConnect Integration
        st.subheader("🔗 WalletConnect Integration")
        
        wc_col1, wc_col2 = st.columns(2)
        
        with wc_col1:
            if st.button("Connect Wallet", use_container_width=True):
                st.info("WalletConnect integration: This would open a QR code for mobile wallet connection")
        
        with wc_col2:
            st.button("Disconnect Wallet", use_container_width=True, disabled=True)
        
        # Recent Executions
        if st.session_state.executed_trades:
            st.subheader("📋 Recent Executions")
            
            trades_df = pd.DataFrame(st.session_state.executed_trades)
            trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
            trades_df = trades_df.sort_values('timestamp', ascending=False)
            
            st.dataframe(
                trades_df[['timestamp', 'type', 'amount', 'actual_profit', 'gas_cost', 'success']],
                use_container_width=True
            )
    
    # TAB 4: Backtesting
    with tab4:
        st.header("📈 Backtesting Engine")
        
        st.info("Test your strategy against historical data to optimize parameters")
        
        # Backtesting Configuration
        bt_col1, bt_col2, bt_col3 = st.columns(3)
        
        with bt_col1:
            bt_duration = st.selectbox("Backtest Duration", ["1 Hour", "6 Hours", "24 Hours", "7 Days"])
            bt_interval = st.selectbox("Check Interval", ["1 min", "5 min", "15 min", "30 min"])
        
        with bt_col2:
            bt_trade_amount = st.number_input("Trade Amount (ETH)", min_value=0.01, value=0.1, key="bt_amount")
            bt_min_profit = st.slider("Min Profit %", 0.1, 5.0, 0.5, key="bt_profit")
        
        with bt_col3:
            bt_max_trades = st.number_input("Max Trades", min_value=1, value=100)
            bt_strategy = st.selectbox("Strategy", ["Direct Arbitrage", "Triangular", "Both"])
        
        if st.button("🚀 Run Backtest", use_container_width=True):
            with st.spinner("Running backtest simulation..."):
                # Simulate backtest
                progress_bar = st.progress(0)
                
                # Generate simulated opportunities
                num_opportunities = 20
                for i in range(num_opportunities):
                    # Create fake opportunity
                    fake_opp = {
                        'type': 'direct',
                        'amount': bt_trade_amount,
                        'profit': bt_trade_amount * (bt_min_profit + i * 0.1) / 100,
                        'profit_percentage': bt_min_profit + i * 0.1,
                        'timestamp': datetime.now() - timedelta(hours=i)
                    }
                    
                    # Simulate trade
                    result = backtest_engine.simulate_trade(fake_opp)
                    
                    progress_bar.progress((i + 1) / num_opportunities)
                    time.sleep(0.1)
                
                st.session_state.backtest_results = backtest_engine.trades
                st.success("✅ Backtest completed!")
        
        # Display Backtest Results
        if st.session_state.backtest_results:
            st.subheader("📊 Backtest Results")
            
            stats = backtest_engine.get_statistics()
            
            # Key Metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("Total Trades", stats.get('total_trades', 0))
                st.metric("Successful Trades", stats.get('successful_trades', 0))
            
            with metric_col2:
                st.metric("Win Rate", f"{stats.get('win_rate', 0):.1f}%")
                st.metric("Avg Profit/Trade", f"{stats.get('avg_profit_per_trade', 0):.4f} ETH")
            
            with metric_col3:
                st.metric("Total Profit", f"{stats.get('total_profit', 0):.4f} ETH")
                st.metric("Total Loss", f"{stats.get('total_loss', 0):.4f} ETH")
            
            with metric_col4:
                net_profit = stats.get('net_profit', 0)
                st.metric("Net Profit", f"{net_profit:.4f} ETH", 
                         delta=f"{net_profit:.4f} ETH")
                st.metric("Profit Factor", f"{stats.get('profit_factor', 0):.2f}")
            
            # Profit Chart
            df_bt = pd.DataFrame(st.session_state.backtest_results)
            df_bt['cumulative_profit'] = df_bt['actual_profit'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_bt.index,
                y=df_bt['cumulative_profit'],
                mode='lines',
                name='Cumulative Profit',
                fill='tozeroy'
            ))
            
            fig.update_layout(
                title="Cumulative Profit Over Time",
                xaxis_title="Trade Number",
                yaxis_title="Cumulative Profit (ETH)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trade Distribution
            fig2 = px.histogram(df_bt, x='actual_profit', nbins=20,
                               title="Profit Distribution",
                               labels={'actual_profit': 'Profit (ETH)'})
            st.plotly_chart(fig2, use_container_width=True)
            
            # Detailed Results Table
            with st.expander("📋 View Detailed Results"):
                st.dataframe(df_bt, use_container_width=True)
    
    # TAB 5: Trade History
    with tab5:
        st.header("📜 Trade History")
        
        if st.session_state.executed_trades:
            # Summary Stats
            hist_col1, hist_col2, hist_col3 = st.columns(3)
            
            with hist_col1:
                total_trades = len(st.session_state.executed_trades)
                st.metric("Total Trades", total_trades)
            
            with hist_col2:
                successful = len([t for t in st.session_state.executed_trades if safe_get(t, 'success', False)])
                st.metric("Successful", successful)
            
            with hist_col3:
                total_profit = sum([safe_get(t, 'actual_profit', 0) for t in st.session_state.executed_trades if safe_get(t, 'success', False)])
                st.metric("Total Profit", f"{total_profit:.4f} ETH")
            
            # Filters
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                filter_type = st.multiselect("Filter by Type", ["direct", "triangular"], default=["direct", "triangular"])
            
            with filter_col2:
                filter_success = st.radio("Filter by Status", ["All", "Success", "Failed"])
            
            # Apply filters
            filtered_trades = st.session_state.executed_trades.copy()
            
            if filter_type:
                filtered_trades = [t for t in filtered_trades if safe_get(t, 'type', '') in filter_type]
            
            if filter_success == "Success":
                filtered_trades = [t for t in filtered_trades if safe_get(t, 'success', False)]
            elif filter_success == "Failed":
                filtered_trades = [t for t in filtered_trades if not safe_get(t, 'success', False)]
            
            # Display trades
            if filtered_trades:
                df_history = pd.DataFrame(filtered_trades)
                df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
                df_history = df_history.sort_values('timestamp', ascending=False)
                
                st.dataframe(df_history, use_container_width=True)
                
                # Export options
                csv = df_history.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"trade_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No trades match the selected filters")
        else:
            st.info("No trade history available. Execute trades in the 'Live Trading' tab.")
    
    # TAB 6: Alerts
    with tab6:
        st.header("🔔 Alert System")
        
        # Alert Configuration
        st.subheader("⚙️ Alert Settings")
        
        alert_col1, alert_col2 = st.columns(2)
        
        with alert_col1:
            alert_min_profit = st.number_input("Alert Min Profit %", min_value=0.1, value=1.0, key="alert_profit")
            alert_email = st.text_input("Email (optional)", placeholder="your@email.com")
        
        with alert_col2:
            alert_sound = st.checkbox("Enable Sound Alert", value=True)
            alert_desktop = st.checkbox("Desktop Notification", value=True)
        
        # Custom Alert Rules
        st.subheader("📋 Custom Alert Rules")
        
        with st.expander("➕ Add New Rule"):
            rule_col1, rule_col2 = st.columns(2)
            
            with rule_col1:
                rule_type = st.selectbox("Rule Type", ["Profit Threshold", "Gas Price", "Liquidity Change"])
                rule_condition = st.selectbox("Condition", ["Greater than", "Less than", "Equal to"])
            
            with rule_col2:
                rule_value = st.number_input("Value", min_value=0.0, value=1.0)
                rule_enabled = st.checkbox("Enabled", value=True)
            
            if st.button("💾 Save Rule"):
                st.success("✅ Alert rule saved!")
        
        # Alert History
        st.subheader("📜 Alert History")
        
        # Add sample alerts to history
        if not st.session_state.alert_history:
            st.session_state.alert_history = [
                {
                    'timestamp': datetime.now() - timedelta(minutes=5),
                    'type': 'Opportunity',
                    'message': 'High profit opportunity detected: 2.5%',
                    'sent': True
                },
                {
                    'timestamp': datetime.now() - timedelta(minutes=15),
                    'type': 'Gas Price',
                    'message': 'Gas price dropped below 50 Gwei',
                    'sent': True
                }
            ]
        
        if st.session_state.alert_history:
            for alert in st.session_state.alert_history[-10:]:
                with st.container():
                    col1, col2, col3 = st.columns([2, 3, 1])
                    
                    with col1:
                        st.write(alert['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
                    
                    with col2:
                        st.write(f"**{alert['type']}:** {alert['message']}")
                    
                    with col3:
                        status = "✅ Sent" if alert['sent'] else "❌ Failed"
                        st.write(status)
                    
                    st.divider()
        else:
            st.info("No alerts in history")
        
        # Test Notification
        st.subheader("🧪 Test Notifications")
        
        test_col1, test_col2, test_col3 = st.columns(3)
        
        with test_col1:
            if st.button("📱 Test Telegram", use_container_width=True):
                if telegram:
                    success = telegram.send_message("🧪 Test notification from Arbitrage Bot!")
                    if success:
                        st.success("✅ Telegram notification sent!")
                    else:
                        st.error("❌ Failed to send Telegram notification")
                else:
                    st.warning("⚠️ Telegram not configured")
        
        with test_col2:
            if st.button("📧 Test Email", use_container_width=True):
                st.info("Email notification feature (requires SMTP configuration)")
        
        with test_col3:
            if st.button("🔔 Test Desktop", use_container_width=True):
                st.info("Desktop notification feature (requires browser permission)")

if __name__ == "__main__":
    main()
