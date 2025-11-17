# 🔧 Troubleshooting Guide

Complete guide untuk mengatasi semua error yang mungkin terjadi.

## 🚨 Quick Diagnostics

**Before reporting issues, run these tests:**

```bash
# Test 1: Check Python version (should be 3.9+)
python --version

# Test 2: Test dependencies
pip list | grep -E "streamlit|web3|pandas|plotly"

# Test 3: Run connection test
python test_connections.py

# Test 4: Run app
streamlit run app.py
```

---

## ❌ Common Errors & Solutions

### 1. KeyError: 'best_profit' or similar

**Error Message:**
```
KeyError: 'best_profit'
File "app.py", line 344
```

**Cause:** Trying to access dictionary key that doesn't exist

**✅ SOLUTION:**
This has been fixed in the latest version. Update your code:

```bash
# Pull latest version
git pull origin main

# Or download latest app.py
```

**Manual Fix:**
The code now uses `safe_get()` function:
```python
profit = safe_get(stats, 'best_profit', 0)  # Returns 0 if key not found
```

---

### 2. Web3RPCError: Cannot fulfill request (-32046)

**Error Message:**
```
web3.exceptions.Web3RPCError: {'code': -32046, 'message': 'Cannot fulfill request'}
```

**Cause:** RPC endpoint can't process the request

**✅ SOLUTIONS:**

**Option 1: Change RPC Provider (Easiest)**
1. Open app in browser
2. Sidebar → Select different RPC from dropdown
3. Try: "Ankr (Fast & Reliable)" or "PublicNode"
4. Click away from dropdown to apply

**Option 2: Enable Auto-Fallback**
1. Sidebar → "Advanced RPC Settings"
2. ✅ Check "Enable Automatic Fallback"
3. App will auto-switch to working RPC

**Option 3: Use RPC Health Check**
1. Sidebar → "Advanced RPC Settings"
2. Click "🏥 Check RPC Health"
3. Wait for results
4. Use the recommended RPC

**Option 4: Premium RPC (Best for production)**
```python
# Get free API key from Alchemy
# Sign up: https://alchemy.com

# In app:
# 1. Select "Custom RPC URL"
# 2. Enter: https://eth-mainnet.g.alchemy.com/v2/YOUR-API-KEY
```

---

### 3. Connection Timeout

**Error Message:**
```
requests.exceptions.ConnectTimeout: HTTPConnectionPool
```

**✅ SOLUTIONS:**

1. **Increase Timeout:**
   - Sidebar → Advanced Settings
   - Increase "Request Timeout" to 20-30 seconds

2. **Try Different RPC:**
   - Some RPCs are faster than others
   - Run `python test_connections.py` to find fastest

3. **Check Internet:**
   ```bash
   ping 8.8.8.8
   ```

4. **Use VPN:**
   - Some RPCs may be geo-blocked
   - Try with VPN enabled

---

### 4. Gas Price Error

**Error Message:**
```
Error fetching gas price
```

**Status:** ✅ Auto-handled by bot

**What Happens:**
- Bot uses default gas prices:
  - Ethereum: 30 Gwei
  - BSC: 5 Gwei
- Shows warning message
- Continues to work normally

**To Fix Properly:**
- Switch to RPC that supports `eth_gasPrice`
- Recommended: Ankr, Alchemy, Infura

---

### 5. Rate Limit Exceeded (-32005)

**Error Message:**
```
web3.exceptions.Web3RPCError: {'code': -32005, 'message': 'Rate limit exceeded'}
```

**✅ SOLUTIONS:**

1. **Reduce Scan Frequency:**
   - Disable "Auto-scan" temporarily
   - Increase scan interval to 60+ seconds

2. **Switch RPC:**
   - Each RPC has separate rate limits
   - Change to different provider

3. **Upgrade to Premium:**
   - Alchemy: 300M requests/month free
   - Infura: 100k requests/day free

---

### 6. Module Not Found

**Error Message:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**✅ SOLUTION:**

```bash
# Install all dependencies
pip install -r requirements.txt

# Or manually:
pip install streamlit web3 pandas plotly requests

# Verify installation:
pip list | grep streamlit
```

---

### 7. Streamlit Not Recognized (Windows)

**Error Message:**
```
'streamlit' is not recognized as an internal or external command
```

**✅ SOLUTIONS:**

**Option 1: Add Python to PATH**
1. Search "Environment Variables" in Windows
2. Edit "Path" variable
3. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts`
4. Restart terminal

**Option 2: Use Python -m**
```bash
python -m streamlit run app.py
```

**Option 3: Full Path**
```bash
C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts\streamlit.exe run app.py
```

---

### 8. Invalid Address

**Error Message:**
```
ValueError: invalid address
```

**✅ SOLUTION:**

Check address format:
- Must start with `0x`
- Must be 42 characters long
- Valid checksum

```python
# Valid:
0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2

# Invalid:
C02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2  # Missing 0x
0xC02aa...  # Too short
```

---

### 9. No Opportunities Found

**Not an error, but common issue**

**✅ SOLUTIONS:**

1. **Lower Profit Threshold:**
   - Sidebar → "Min Profit %"
   - Try 0.3% or 0.5%

2. **Try Different Token Pairs:**
   - High volume pairs work better
   - Try: WETH/USDC, WETH/USDT

3. **Check During High Volatility:**
   - More opportunities during:
     - Major news events
     - High trading volume
     - Market dumps/pumps

4. **Use Triangular Arbitrage:**
   - Click "Scan Triangular Arbitrage"
   - More paths = more opportunities

5. **Increase Trade Amount:**
   - Larger amounts may show more opportunities
   - But start small for testing!

---

### 10. Transaction Failed

**When trying to execute trades**

**✅ CHECKLIST:**

- [ ] Sufficient balance for trade
- [ ] Sufficient balance for gas
- [ ] Token approved for trading
- [ ] Slippage tolerance adequate
- [ ] Gas price not too low
- [ ] Private key correct
- [ ] Network matches tokens

---

## 🧪 Testing Checklist

Before reporting bugs, verify:

```bash
# 1. Test RPC connections
python test_connections.py

# 2. Check if app starts
streamlit run app.py

# 3. In browser:
✅ App loads without errors
✅ Network selection works
✅ RPC connection successful
✅ Wallet balance shows (if address entered)
✅ Gas price shows or "N/A" displayed
✅ Token dropdowns work
✅ Scan buttons respond

# 4. Test basic functionality
✅ Select token pair
✅ Click "Scan Direct Arbitrage"
✅ Either finds opportunities OR shows "No opportunities"
✅ No crashes or errors
```

---

## 🐛 Still Having Issues?

### Debug Mode

Enable detailed logging:

```python
# Add to top of app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Collect Information

When reporting issues, include:

1. **Error message** (full text)
2. **Python version** (`python --version`)
3. **OS** (Windows/Mac/Linux)
4. **RPC provider** used
5. **Network** (Ethereum/BSC)
6. **Steps to reproduce**

### Example Bug Report

```
Title: KeyError when viewing backtest results

Description:
- Ran backtest with 20 trades
- Clicked to view results
- Got KeyError: 'best_profit'

Environment:
- Python 3.12
- Windows 11
- Using Ankr RPC (Ethereum)
- App version: latest from GitHub

Error:
```python
KeyError: 'best_profit'
File "app.py", line 344
    stats['best_profit']
```

Steps to reproduce:
1. Go to Backtesting tab
2. Set duration to 1 hour
3. Click "Run Backtest"
4. Wait for completion
5. Error appears when displaying results
```

---

## 📞 Getting Help

### Support Channels

1. **GitHub Issues**: https://github.com/YOUR_REPO/issues
2. **Telegram**: @your_telegram_group
3. **Discord**: Your Discord link
4. **Email**: support@yourdomain.com

### Before Asking

1. ✅ Read this guide
2. ✅ Run `test_connections.py`
3. ✅ Check GitHub issues for similar problems
4. ✅ Try basic solutions first

### Response Time

- GitHub Issues: 24-48 hours
- Telegram/Discord: Few hours
- Email: 1-3 business days

---

## 🎓 Preventive Measures

### Best Practices

1. **Always Enable Auto-Fallback**
   - Prevents single point of failure
   - Automatic recovery

2. **Test Before Live Trading**
   - Use small amounts
   - Verify everything works
   - Check gas calculations

3. **Monitor RPC Health**
   - Run health check regularly
   - Switch if response time degrades

4. **Keep Updated**
   ```bash
   git pull origin main
   pip install -r requirements.txt --upgrade
   ```

5. **Use Premium RPC for Production**
   - More reliable
   - Better support
   - Higher rate limits

### Maintenance

**Weekly:**
- [ ] Check for updates
- [ ] Run RPC health check
- [ ] Review error logs

**Monthly:**
- [ ] Update dependencies
- [ ] Check token addresses still valid
- [ ] Review and optimize strategy

---

## 🔬 Advanced Troubleshooting

### Network Tab (Browser)

1. Open browser DevTools (F12)
2. Go to "Network" tab
3. Look for failed requests (red)
4. Check response messages

### Streamlit Cache Issues

```bash
# Clear Streamlit cache
streamlit cache clear

# Or manually delete:
rm -rf ~/.streamlit/cache
```

### Python Environment Issues

```bash
# Create fresh virtual environment
python -m venv venv_new
source venv_new/bin/activate  # Linux/Mac
# or
venv_new\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Test
streamlit run app.py
```

### Port Already in Use

```bash
# Kill existing Streamlit
pkill -f streamlit  # Linux/Mac
taskkill /F /IM streamlit.exe  # Windows

# Or use different port
streamlit run app.py --server.port 8502
```

---

## ✅ Success Indicators

You know it's working when:

- ✅ App loads without errors
- ✅ Green "Connected to ETHEREUM/BSC" in sidebar
- ✅ Block number displays
- ✅ Gas price shows (or graceful "N/A")
- ✅ Scan finds opportunities (or clearly states none found)
- ✅ No red error messages
- ✅ Charts and tables render properly

---

**Last Updated:** November 2024

**Questions?** Open an issue or ask in community!
