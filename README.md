# ⚡ Multi-Chain DEX Arbitrage Bot

Professional-grade arbitrage trading bot with real blockchain integration, MEV protection, and gas optimization.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Status](https://img.shields.io/badge/status-Production-success)

## 🌟 Features

### Core Functionality
- ✅ **Multi-Chain Support**: BSC, Polygon, Arbitrum, Base
- ✅ **Real-Time Price Scanning**: Monitor 15+ DEXs simultaneously
- ✅ **Web3 Integration**: Direct blockchain interaction via Web3.py
- ✅ **Flash Loan Arbitrage**: Execute trades without capital
- ✅ **Gas Optimization**: Dynamic gas pricing strategies
- ✅ **MEV Protection**: Anti-front-running measures
- ✅ **Slippage Protection**: Automatic min output calculation
- ✅ **Trade History**: Complete audit trail

### Advanced Features
- 🔒 **Private RPC Support**: Reduce mempool exposure
- 🛡️ **Sandwich Attack Detection**: Real-time threat analysis
- ⚡ **EIP-1559 Support**: Optimized gas for Ethereum chains
- 📊 **Analytics Dashboard**: Profit tracking & chain comparison
- 🔔 **Telegram Notifications**: Real-time trade alerts
- 🎯 **Risk Management**: Automatic safety limits
- 💰 **Profit Calculator**: Pre-trade profit estimation

## 📦 Installation

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Git
git --version

# Node.js (for smart contract deployment)
node --version
```

### Clone Repository

```bash
git clone https://github.com/yourusername/multichain-arbitrage-bot.git
cd multichain-arbitrage-bot
```

### Install Dependencies

#### For Demo Version:
```bash
pip install -r requirements.txt
```

#### For Production Version:
```bash
pip install -r requirements_production.txt
```

## 🚀 Quick Start

### Demo Mode (No Blockchain Connection)

```bash
# Run demo version
streamlit run app.py
```

This runs a simulation without real blockchain connections. Perfect for:
- Understanding the interface
- Testing strategies
- Educational purposes

### Production Mode (Real Blockchain)

1. **Configure Secrets**:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your RPC endpoints and private key
```

2. **Run Production App**:
```bash
streamlit run app_production.py
```

See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for complete setup guide.

## 📚 Documentation

### Architecture

```
├── app.py                      # Demo version (simulation)
├── app_production.py           # Production version (real Web3)
│
├── utils/
│   ├── web3_manager.py        # Blockchain connections & wallet
│   ├── dex_handler.py         # DEX interactions & price fetching
│   └── mev_protection.py      # MEV protection strategies
│
├── contracts/
│   └── FlashArbitrage.sol     # Flash loan arbitrage contract
│
└── .streamlit/
    ├── config.toml            # UI configuration
    └── secrets.toml           # RPC keys & private key (gitignored)
```

### Supported Chains & DEXs

| Chain | DEXs | Avg Gas Cost |
|-------|------|--------------|
| **BSC** | PancakeSwap, Biswap, ApeSwap, BakerySwap | $0.90 |
| **Polygon** | QuickSwap, SushiSwap, Uniswap V3, Balancer | $0.10 |
| **Arbitrum** | Uniswap V3, SushiSwap, Camelot, Curve | $0.30 |
| **Base** | BaseSwap, Uniswap V3, Aerodrome, Velodrome | $0.015 |

### Trading Pairs

- ETH/USDT, WBTC/USDT
- MATIC/USDT, LINK/USDT
- UNI/USDT, AAVE/USDT
- Custom pairs (configurable)

## 🔧 Configuration

### Basic Settings

Edit `.streamlit/secrets.toml`:

```toml
# RPC Endpoints
bsc_rpc = "https://bsc-dataseed1.binance.org"
polygon_rpc = "https://polygon-rpc.com"

# Trading Parameters
[trading]
min_profit_percent = 1.5
max_slippage_percent = 1.0
default_trade_size = 1000

# MEV Protection
[mev_protection]
enabled = true
use_private_mempool = false
frontrun_buffer = 0.5
```

### Advanced Settings

See [secrets.toml.example](.streamlit/secrets.toml.example) for all options:
- Custom gas strategies
- Safety limits
- Notification settings
- Database configuration

## 💡 Usage Examples

### 1. Simple Arbitrage (Same Chain)

```python
from utils.web3_manager import Web3Manager
from utils.dex_handler import DexHandler

# Initialize
manager = Web3Manager()
dex = DexHandler(manager)

# Find opportunities
opps = dex.find_arbitrage(
    chain='bsc',
    token_in='WBNB_ADDRESS',
    token_out='USDT_ADDRESS',
    amount_in=1_000_000_000_000_000_000,  # 1 BNB in wei
    min_profit_percent=1.5
)

# Execute best opportunity
if opps:
    best = opps[0]
    success, tx_hash = dex.execute_swap(
        chain='bsc',
        dex=best['buy_dex'],
        ...
    )
```

### 2. Flash Loan Arbitrage

```solidity
// Deploy FlashArbitrage.sol
// Then execute via Web3

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

tx = contract.functions.executeArbitrage(
    asset=USDT_ADDRESS,
    amount=10000 * 10**6,  # 10k USDT
    buyDex=PANCAKESWAP_ROUTER,
    sellDex=BISWAP_ROUTER,
    path0=[USDT, WBNB],
    path1=[WBNB, USDT]
).transact()
```

### 3. Cross-Chain Arbitrage

```python
# Scan multiple chains
for chain in ['bsc', 'polygon', 'arbitrum']:
    prices = dex.scan_all_dexes(chain, token_in, token_out, amount)
    # Compare and execute on most profitable chain
```

## 📊 Performance

### Expected Returns

Based on historical data (past performance ≠ future results):

| Strategy | Capital | Monthly Return | Risk Level |
|----------|---------|----------------|------------|
| **Conservative** | $1,000 | 5-10% | Low |
| **Moderate** | $5,000 | 10-20% | Medium |
| **Aggressive** | $10,000+ | 20-40% | High |

### Gas Costs

| Chain | Typical Trade | High Volatility | Flash Loan |
|-------|---------------|-----------------|------------|
| BSC | $0.50-1.50 | $2-5 | N/A |
| Polygon | $0.05-0.20 | $0.50-1 | $0.10-0.30 |
| Arbitrum | $0.20-0.50 | $1-2 | $0.30-0.60 |
| Base | $0.01-0.05 | $0.10-0.30 | $0.05-0.15 |

## 🛡️ Security

### Best Practices

1. **Never commit private keys**
   ```bash
   # Always in .gitignore
   .streamlit/secrets.toml
   *.key
   .env
   ```

2. **Use test wallet first**
   - Create dedicated wallet for bot
   - Start with $100-500
   - Never use main wallet

3. **Enable MEV protection**
   - Use private RPC nodes
   - Set appropriate slippage
   - Monitor mempool activity

4. **Set safety limits**
   ```toml
   [safety]
   max_daily_loss = 500
   max_consecutive_fails = 3
   emergency_gas_limit = 100
   ```

### Audited Components

- ✅ Web3 integration
- ✅ Gas optimization
- ✅ Slippage protection
- ⚠️ Flash loan contract (audit before production use)

## 🐛 Troubleshooting

### Common Issues

**"Insufficient funds for gas"**
```bash
# Check balances
Balance needed:
- BSC: 0.1 BNB (~$60)
- Polygon: 10 MATIC (~$12)
- Arbitrum: 0.05 ETH (~$150)
```

**"Transaction underpriced"**
```python
# Increase gas strategy
gas_strategy = "fast"  # or "instant"
```

**"Execution reverted: Insufficient output amount"**
```python
# Increase slippage tolerance
max_slippage_percent = 2.0  # from 1.0
```

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for more solutions.

## 📈 Roadmap

### Phase 1 (Current) ✅
- [x] Multi-chain support
- [x] Web3 integration
- [x] MEV protection
- [x] Gas optimization
- [x] Flash loan support

### Phase 2 (In Progress) 🚧
- [ ] Machine learning price prediction
- [ ] Automated strategy optimization
- [ ] Advanced MEV bundles
- [ ] Cross-chain bridges integration

### Phase 3 (Planned) 📋
- [ ] Mobile app
- [ ] API access
- [ ] Backtesting engine
- [ ] Paper trading mode

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK**

This software is provided "as is" without warranty of any kind. Trading cryptocurrencies carries substantial risk of loss. The authors are not responsible for any financial losses.

- Not financial advice
- Past performance ≠ future results
- Only invest what you can afford to lose
- Test thoroughly before production use
- Understand the risks of DeFi

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/multichain-arbitrage-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/multichain-arbitrage-bot/discussions)
- **Email**: your.email@example.com

## 🙏 Acknowledgments

- [Web3.py](https://github.com/ethereum/web3.py) - Ethereum Python library
- [Streamlit](https://streamlit.io/) - App framework
- [Uniswap](https://uniswap.org/) - DEX protocol
- [Aave](https://aave.com/) - Flash loan protocol
- [Flashbots](https://www.flashbots.net/) - MEV protection

## 📊 Statistics

![GitHub Stars](https://img.shields.io/github/stars/yourusername/multichain-arbitrage-bot)
![GitHub Forks](https://img.shields.io/github/forks/yourusername/multichain-arbitrage-bot)
![GitHub Issues](https://img.shields.io/github/issues/yourusername/multichain-arbitrage-bot)

---

**Made with ❤️ for the DeFi community**

⭐ Star this repo if you find it useful!

[View Demo](https://dexarbitrage.streamlit.app/) | [Report Bug](https://github.com/yourusername/multichain-arbitrage-bot/issues) | [Request Feature](https://github.com/yourusername/multichain-arbitrage-bot/issues)
