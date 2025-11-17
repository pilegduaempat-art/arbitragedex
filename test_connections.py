"""
Test script to verify RPC connections and basic functionality
Run this before starting the main app to check everything works
"""

from web3 import Web3
import time

# Free RPC Endpoints
RPCS = {
    "ethereum": [
        "https://eth.public-rpc.com",
        "https://rpc.ankr.com/eth",
        "https://cloudflare-eth.com",
        "https://ethereum.publicnode.com",
    ],
    "bsc": [
        "https://bsc.public-rpc.com",
        "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed.binance.org",
        "https://bsc.publicnode.com",
    ]
}

def test_rpc(url, timeout=5):
    """Test single RPC endpoint"""
    print(f"\n🔍 Testing: {url}")
    
    try:
        start = time.time()
        w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': timeout}))
        
        # Test connection
        if not w3.is_connected():
            print("   ❌ Connection failed")
            return False
        
        # Test block number
        try:
            block = w3.eth.block_number
            response_time = (time.time() - start) * 1000
            print(f"   ✅ Connected! Block: {block:,}")
            print(f"   ⚡ Response time: {response_time:.0f}ms")
        except Exception as e:
            print(f"   ⚠️  Connected but can't fetch block: {str(e)[:50]}")
            return False
        
        # Test gas price
        try:
            gas = w3.eth.gas_price
            gas_gwei = w3.from_wei(gas, 'gwei')
            print(f"   ⛽ Gas price: {gas_gwei:.1f} Gwei")
        except Exception as e:
            print(f"   ⚠️  Gas price unavailable: {str(e)[:50]}")
            print("   💡 App will use default gas prices")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def test_network(network_name):
    """Test all RPCs for a network"""
    print(f"\n{'='*60}")
    print(f"Testing {network_name.upper()} RPCs")
    print('='*60)
    
    working_rpcs = []
    
    for url in RPCS[network_name]:
        if test_rpc(url):
            working_rpcs.append(url)
    
    print(f"\n📊 Results for {network_name.upper()}:")
    print(f"   Working RPCs: {len(working_rpcs)}/{len(RPCS[network_name])}")
    
    if working_rpcs:
        print(f"\n✅ Recommended RPC: {working_rpcs[0]}")
    else:
        print("\n❌ No working RPCs found!")
        print("💡 Try using premium RPC (Alchemy/Infura)")
    
    return working_rpcs

def test_contract_call():
    """Test actual DEX contract call"""
    print(f"\n{'='*60}")
    print("Testing Smart Contract Calls")
    print('='*60)
    
    # Uniswap V2 Router on Ethereum
    UNISWAP_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    
    ROUTER_ABI = [{
        "inputs": [{"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                   {"internalType": "address[]", "name": "path", "type": "address[]"}],
        "name": "getAmountsOut",
        "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    }]
    
    print("\n🔍 Testing Uniswap V2 price query...")
    
    try:
        # Use first working Ethereum RPC
        w3 = Web3(Web3.HTTPProvider(RPCS['ethereum'][0]))
        
        if not w3.is_connected():
            print("❌ Cannot connect to Ethereum")
            return False
        
        router = w3.eth.contract(
            address=Web3.to_checksum_address(UNISWAP_ROUTER),
            abi=ROUTER_ABI
        )
        
        # Query price for 1 ETH -> USDC
        amount_in = w3.to_wei(1, 'ether')
        path = [
            Web3.to_checksum_address(WETH),
            Web3.to_checksum_address(USDC)
        ]
        
        amounts = router.functions.getAmountsOut(amount_in, path).call()
        
        usdc_out = amounts[1] / 1e6  # USDC has 6 decimals
        
        print(f"✅ Contract call successful!")
        print(f"   1 ETH = {usdc_out:,.2f} USDC")
        print(f"   This means the bot can query DEX prices!")
        
        return True
        
    except Exception as e:
        print(f"❌ Contract call failed: {str(e)[:100]}")
        print("💡 This might affect arbitrage detection")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 DEX Arbitrage Bot - Connection Test")
    print("="*60)
    
    # Test Ethereum
    eth_rpcs = test_network('ethereum')
    
    # Test BSC
    bsc_rpcs = test_network('bsc')
    
    # Test contract calls
    contract_ok = test_contract_call()
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 SUMMARY")
    print('='*60)
    
    print(f"✅ Ethereum RPCs: {len(eth_rpcs)} working")
    print(f"✅ BSC RPCs: {len(bsc_rpcs)} working")
    print(f"{'✅' if contract_ok else '❌'} Contract calls: {'Working' if contract_ok else 'Failed'}")
    
    if len(eth_rpcs) > 0 or len(bsc_rpcs) > 0:
        print("\n🎉 Ready to run the bot!")
        print("\nRun: streamlit run app.py")
    else:
        print("\n⚠️  No working RPCs found!")
        print("\n💡 Solutions:")
        print("   1. Check your internet connection")
        print("   2. Try using VPN")
        print("   3. Use premium RPC (Alchemy/Infura)")
        print("   4. Wait and try again later")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
