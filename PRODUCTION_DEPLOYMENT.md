# 🚀 Production Deployment Guide

Complete guide untuk deploy production-ready arbitrage bot dengan Web3 integration.

## 📋 Prerequisites

### Required Accounts:
1. **RPC Provider** (pilih salah satu):
   - [Alchemy](https://www.alchemy.com/) - Recommended ⭐
   - [Infura](https://infura.io/)
   - [QuickNode](https://www.quicknode.com/)
   - [NodeReal](https://nodereal.io/)

2. **GitHub Account** untuk deployment

3. **Test Wallet** dengan small funds untuk testing

### Required Knowledge:
- Basic Solidity (untuk smart contracts)
- Web3.py fundamentals
- Gas optimization concepts
- MEV/Front-running awareness

## 🔧 Step 1: Setup RPC Nodes

### Get Free API Keys:

#### Alchemy (Recommended):
```bash
1. Sign up at https://www.alchemy.com/
2. Create App:
   - Name: "Arbitrage Bot"
   - Chain: BSC / Polygon / Arbitrum / Base
   - Network: Mainnet
3. Copy API Key
4. Your RPC URL: https://CHAIN-mainnet.g.alchemy.com/v2/YOUR_API_KEY
```

#### Multiple Chains Example:
```bash
BSC:      https://bsc-mainnet.nodereal.io/v1/YOUR_KEY
Polygon:  https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
Arbitrum: https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY
Base:     https://base-mainnet.g.alchemy.com/v2/YOUR_KEY
```

## 📁 Step 2: File Structure

Create this structure:

```
multichain-arbitrage-bot/
│
├── .streamlit/
│   ├── config.toml
│   ├── secrets.toml          # ⚠️ NEVER commit this!
│   └── secrets.toml.example
│
├── utils/
│   ├── __init__.py
│   ├── web3_manager.py
│   ├── dex_handler.py
│   └── mev_protection.py
│
├── contracts/
│   ├── FlashArbitrage.sol
│   ├── deploy.py
│   └── README.md
│
├── app.py                    # Demo version
├── app_production.py         # Production version
├── requirements_production.txt
├── README.md
├── PRODUCTION_DEPLOYMENT.md
└── .gitignore
```

## 🔐 Step 3: Configure Secrets

### Create `.streamlit/secrets.toml`:

```toml
# Copy from secrets.toml.example and fill with real values

# RPC Endpoints
bsc_rpc = "https://bsc-mainnet.nodereal.io/v1/YOUR_API_KEY"
polygon_rpc = "https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
arbitrum_rpc = "https://arb-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
base_rpc = "https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

# Test Wallet (USE TEST WALLET ONLY!)
private_key = "your_test_wallet_private_key_here"

[trading]
min_profit_percent = 1.5
max_slippage_percent = 1.0
default_trade_size = 1000
max_trade_size = 10000
gas_strategy = "fast"

[mev_protection]
enabled = true
use_private_mempool = false
random_delay_min = 1
random_delay_max = 5
frontrun_buffer = 0.5

[safety]
max_daily_loss = 500
max_consecutive_fails = 3
min_wallet_balance_bnb = 0.1
min_wallet_balance_matic = 10
min_wallet_balance_eth = 0.05
```

### ⚠️ Security Best Practices:

1. **Never commit secrets.toml to GitHub!**
   ```bash
   echo ".streamlit/secrets.toml" >> .gitignore
   ```

2. **Use test wallet only!**
   - Create new wallet specifically for testing
   - Fund with $100-500 max
   - Never use your main wallet

3. **Rotate keys regularly**
   - Change RPC keys monthly
   - Use different keys for dev/prod

## 📦 Step 4: Install Dependencies

### Update `requirements_production.txt`:

```txt
streamlit==1.31.0
pandas==2.1.4
plotly==5.18.0
numpy==1.26.3
web3==6.15.1
eth-account==0.11.0
python-dotenv==1.0.0
requests==2.31.0
```

### Install:

```bash
pip install -r requirements_production.txt
```

## 🔨 Step 5: Deploy Smart Contracts (Optional)

### For Flash Loan Arbitrage:

1. **Install Hardhat**:
```bash
npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers
```

2. **Create `hardhat.config.js`**:
```javascript
require("@nomiclabs/hardhat-ethers");

module.exports = {
  solidity: "0.8.19",
  networks: {
    polygon: {
      url: process.env.POLYGON_RPC,
      accounts: [process.env.PRIVATE_KEY]
    },
    arbitrum: {
      url: process.env.ARBITRUM_RPC,
      accounts: [process.env.PRIVATE_KEY]
    },
    base: {
      url: process.env.BASE_RPC,
      accounts: [process.env.PRIVATE_KEY]
    }
  }
};
```

3. **Deploy**:
```bash
npx hardhat run contracts/deploy.py --network polygon
```

4. **Add contract address to secrets.toml**:
```toml
[contracts]
polygon_flash_arbitrage = "0xYOUR_CONTRACT_ADDRESS"
```

## 🧪 Step 6: Local Testing

### Test Web3 Connections:

```python
# test_connections.py
from utils.web3_manager import Web3Manager

manager = Web3Manager()

chains = ['bsc', 'polygon', 'arbitrum', 'base']
for chain in chains:
    w3 = manager.get_web3(chain)
    if w3:
        block = w3.eth.block_number
        print(f"✅ {chain}: Block {block}")
    else:
        print(f"❌ {chain}: Failed")
```

Run:
```bash
python test_connections.py
```

### Test DEX Price Fetching:

```python
# test_dex.py
from utils.web3_manager import Web3Manager
from utils.dex_handler import DexHandler

manager = Web3Manager()
dex = DexHandler(manager)

# Test get price
price = dex.get_price(
    chain='bsc',
    dex='pancakeswap',
    token_in='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',  # WBNB
    token_out='0x55d398326f99059fF775485246999027B3197955',  # USDT
    amount_in=1000000000000000000  # 1 BNB in wei
)

print(f"1 BNB = {price / 1e18} USDT")
```

### Run Local Streamlit:

```bash
streamlit run app_production.py
```

Open http://localhost:8501

## 🌐 Step 7: Deploy to Streamlit Cloud

### Option A: Demo Version (Safe):

1. Push to GitHub:
```bash
git add app.py requirements.txt
git commit -m "Add demo version"
git push origin main
```

2. Deploy on Streamlit Cloud:
   - Go to share.streamlit.io
   - Select `app.py` (demo version)
   - No secrets needed

### Option B: Production Version (With Web3):

1. Push code (without secrets!):
```bash
git add app_production.py requirements_production.txt utils/
git commit -m "Add production version"
git push origin main
```

2. Deploy on Streamlit Cloud:
   - Select `app_production.py`
   - Add secrets in dashboard

3. Add Secrets in Streamlit Cloud:
   - Go to app settings
   - Click "Secrets"
   - Paste entire `secrets.toml` content
   - Click "Save"

## 🔒 Step 8: Security Hardening

### Enable 2FA on All Accounts:
- GitHub
- RPC Provider (Alchemy/Infura)
- Email

### IP Whitelisting (if available):
```bash
# In RPC provider dashboard
Add your server IP to whitelist
```

### Rate Limiting:
```python
# In web3_manager.py
import time

class Web3Manager:
    def __init__(self):
        self.last_request = {}
        self.min_interval = 0.1  # 100ms between requests
    
    def rate_limit(self, chain):
        now = time.time()
        last = self.last_request.get(chain, 0)
        
        if now - last < self.min_interval:
            time.sleep(self.min_interval - (now - last))
        
        self.last_request[chain] = time.time()
```

## 📊 Step 9: Monitoring & Alerts

### Setup Telegram Notifications:

1. Create bot with @BotFather
2. Get bot token
3. Get your chat ID
4. Add to secrets:
```toml
[notifications]
telegram_enabled = true
telegram_bot_token = "YOUR_BOT_TOKEN"
telegram_chat_id = "YOUR_CHAT_ID"
```

### Implement Alerts:

```python
# utils/notifications.py
import requests
import streamlit as st

def send_telegram(message):
    token = st.secrets["notifications"]["telegram_bot_token"]
    chat_id = st.secrets["notifications"]["telegram_chat_id"]
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    requests.post(url, data=data)

# Usage
send_telegram("🚀 Arbitrage opportunity found! Profit: $50")
```

## 🎯 Step 10: Go Live Checklist

### Before Going Live:

- [ ] All RPC connections working
- [ ] Test wallet funded with small amount
- [ ] Smart contracts deployed (if using flash loans)
- [ ] MEV protection configured
- [ ] Gas optimization tested
- [ ] Notifications working
- [ ] Safety limits configured
- [ ] Emergency stop mechanism ready
- [ ] Logged all test transactions
- [ ] Verified on block explorer

### Start Small:
```toml
# Conservative settings for first 24 hours
[trading]
min_profit_percent = 2.0      # Higher threshold
default_trade_size = 100      # Small size
max_trade_size = 500          # Low limit
gas_strategy = "medium"       # Not too aggressive

[safety]
max_daily_loss = 50           # Stop early if losing
max_consecutive_fails = 2     # Be cautious
```

### Monitor First 24 Hours:
- Check every 2-4 hours
- Review all transactions on block explorer
- Monitor gas costs
- Track actual vs expected profits
- Adjust parameters based on results

## 📈 Step 11: Scaling Up

### After Successful Testing (1-2 weeks):

1. **Increase Trade Size Gradually**:
   ```
   Week 1: $100-500 per trade
   Week 2: $500-1000 per trade
   Week 3: $1000-2000 per trade
   ```

2. **Add More Chains**:
   - Start with 1-2 chains
   - Add more after mastering first chains
   - Each chain has unique quirks

3. **Optimize Gas**:
   - Analyze historical gas usage
   - Find optimal times to trade
   - Consider Layer 2 solutions

4. **Implement Advanced Features**:
   - Flash loans
   - Multi-hop arbitrage
   - Cross-chain bridges
   - MEV bundles (Flashbots)

## 🐛 Troubleshooting

### Common Issues:

#### 1. "Insufficient Funds for Gas"
```python
# Check balances
balance = web3_manager.get_balance('bsc', wallet_address)
print(f"Balance: {balance} BNB")

# Minimum recommended:
# BSC: 0.1 BNB (~$60)
# Polygon: 10 MATIC (~$12)
# Arbitrum: 0.05 ETH (~$150)
```

#### 2. "Transaction Underpriced"
```python
# Increase gas price
gas_strategy = "fast"  # or "instant"
```

#### 3. "Execution Reverted"
```python
# Common causes:
# - Slippage too tight
# - Price changed
# - Insufficient allowance
# - Pair liquidity too low
```

#### 4. "RPC Rate Limit Exceeded"
```python
# Solution: Upgrade to paid plan or add delays
time.sleep(0.1)  # 100ms between requests
```

## 📞 Support & Resources

### Documentation:
- Web3.py: https://web3py.readthedocs.io/
- Uniswap: https://docs.uniswap.org/
- Aave: https://docs.aave.com/
- Flashbots: https://docs.flashbots.net/

### Communities:
- Discord: DeFi Developers
- Telegram: MEV Research
- Reddit: r/ethdev, r/CryptoCurrency

### Block Explorers:
- BSC: https://bscscan.com
- Polygon: https://polygonscan.com
- Arbitrum: https://arbiscan.io
- Base: https://basescan.org

## ⚠️ Final Warning

**This is real money. Real risks.**

- Start small
- Test thoroughly
- Never invest more than you can afford to lose
- Gas fees can be expensive
- Arbitrage opportunities are competitive
- MEV bots may front-run you
- Smart contract bugs can cause total loss
- Market conditions change rapidly

**Not Financial Advice. DYOR (Do Your Own Research).**

---

Good luck! 🚀
