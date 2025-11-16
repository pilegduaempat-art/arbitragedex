import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import random
from typing import Dict, List
import json
import streamlit as st

st.write("🔍 Checking dependencies...")

try:
    import plotly
    st.success(f"✅ Plotly {plotly.__version__} installed")
except Exception as e:
    st.error(f"❌ Plotly error: {e}")
    st.stop()

try:
    import pandas
    st.success(f"✅ Pandas {pandas.__version__} installed")
except Exception as e:
    st.error(f"❌ Pandas error: {e}")

try:
    import numpy
    st.success(f"✅ NumPy {numpy.__version__} installed")
except Exception as e:
    st.error(f"❌ NumPy error: {e}")

st.write("✅ All dependencies OK! Continuing to app...")
st.divider()

# Your normal app code below...
# Page configuration
st.set_page_config(
    page_title="Multi-Chain DEX Arbitrage Bot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .opportunity-card {
        background: #1e1e1e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .chain-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .profit-positive {
        color: #10b981;
        font-weight: bold;
    }
    .profit-negative {
        color: #ef4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Chain Configuration
CHAIN_CONFIG = {
    'bsc': {
        'name': 'BSC',
        'color': '#F3BA2F',
        'icon': '🟡',
        'dexes': ['PancakeSwap', 'Biswap', 'ApeSwap', 'BakerySwap'],
        'avg_gas': 0.003,
        'block_time': 3,
        'native_token': 'BNB',
        'native_price': 600
    },
    'polygon': {
        'name': 'Polygon',
        'color': '#8247E5',
        'icon': '🟣',
        'dexes': ['QuickSwap', 'SushiSwap', 'Uniswap V3', 'Balancer'],
        'avg_gas': 0.001,
        'block_time': 2,
        'native_token': 'MATIC',
        'native_price': 1.2
    },
    'arbitrum': {
        'name': 'Arbitrum',
        'color': '#28A0F0',
        'icon': '🔵',
        'dexes': ['Uniswap V3', 'SushiSwap', 'Camelot', 'Curve'],
        'avg_gas': 0.0005,
        'block_time': 0.25,
        'native_token': 'ETH',
        'native_price': 3000
    },
    'base': {
        'name': 'Base',
        'color': '#0052FF',
        'icon': '🔷',
        'dexes': ['BaseSwap', 'Uniswap V3', 'Aerodrome', 'Velodrome'],
        'avg_gas': 0.0003,
        'block_time': 2,
        'native_token': 'ETH',
        'native_price': 3000
    }
}

TRADING_PAIRS = ['ETH/USDT', 'WBTC/USDT', 'MATIC/USDT', 'LINK/USDT', 'UNI/USDT', 'AAVE/USDT']

# Initialize session state
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'opportunities' not in st.session_state:
    st.session_state.opportunities = []
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []
if 'total_profit' not in st.session_state:
    st.session_state.total_profit = 0
if 'chain_stats' not in st.session_state:
    st.session_state.chain_stats = {chain: {'total': 0, 'viable': 0, 'avg_profit': 0} for chain in CHAIN_CONFIG.keys()}

# Helper Functions
def calculate_gas_cost(chain: str, token_price: float) -> float:
    """Calculate gas cost in USD"""
    config = CHAIN_CONFIG[chain]
    gas_units = 250000  # typical swap
    gas_cost = (gas_units * config['avg_gas'] * 1e-9) * config['native_price']
    return gas_cost

def generate_price(pair: str) -> float:
    """Generate realistic price for trading pair"""
    base_prices = {
        'ETH/USDT': 3000,
        'WBTC/USDT': 65000,
        'MATIC/USDT': 1.2,
        'LINK/USDT': 15,
        'UNI/USDT': 8,
        'AAVE/USDT': 180
    }
    base = base_prices.get(pair, 100)
    return base * (1 + random.uniform(-0.02, 0.02))

def generate_arbitrage_opportunity(settings: Dict) -> Dict:
    """Generate single arbitrage opportunity"""
    chain = random.choice(settings['enabled_chains'])
    config = CHAIN_CONFIG[chain]
    pair = random.choice(settings['trading_pairs'])
    
    dex1 = random.choice(config['dexes'])
    dex2 = random.choice([d for d in config['dexes'] if d != dex1])
    
    price1 = generate_price(pair)
    price_diff = random.uniform(-1, 3)  # -1% to +3%
    price2 = price1 * (1 + price_diff / 100)
    
    # Calculate profits
    gross_profit_pct = abs(price_diff)
    gas_cost_usd = calculate_gas_cost(chain, price1)
    gas_cost_pct = (gas_cost_usd / settings['trade_size']) * 100
    slippage = 0.5  # 0.5%
    
    net_profit_pct = gross_profit_pct - gas_cost_pct - slippage
    net_profit_usd = (net_profit_pct / 100) * settings['trade_size']
    
    return {
        'chain': chain,
        'chain_name': config['name'],
        'chain_icon': config['icon'],
        'pair': pair,
        'dex1': dex1,
        'dex2': dex2,
        'price1': round(price1, 2),
        'price2': round(price2, 2),
        'gross_profit_pct': round(gross_profit_pct, 3),
        'gas_cost_usd': round(gas_cost_usd, 4),
        'gas_cost_pct': round(gas_cost_pct, 3),
        'net_profit_pct': round(net_profit_pct, 3),
        'net_profit_usd': round(net_profit_usd, 2),
        'is_viable': net_profit_pct > settings['min_profit'],
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }

def scan_opportunities(settings: Dict) -> List[Dict]:
    """Scan all chains for opportunities"""
    opportunities = []
    for _ in range(random.randint(5, 12)):
        opp = generate_arbitrage_opportunity(settings)
        opportunities.append(opp)
    return sorted(opportunities, key=lambda x: x['net_profit_pct'], reverse=True)

def calculate_chain_stats(opportunities: List[Dict]) -> Dict:
    """Calculate statistics per chain"""
    stats = {}
    for chain in CHAIN_CONFIG.keys():
        chain_opps = [o for o in opportunities if o['chain'] == chain]
        viable_opps = [o for o in chain_opps if o['is_viable']]
        
        stats[chain] = {
            'total': len(chain_opps),
            'viable': len(viable_opps),
            'avg_profit': round(sum(o['net_profit_pct'] for o in viable_opps) / len(viable_opps), 2) if viable_opps else 0,
            'best_profit': round(max((o['net_profit_pct'] for o in viable_opps), default=0), 2),
            'total_potential': round(sum(o['net_profit_usd'] for o in viable_opps), 2)
        }
    return stats

def execute_trade(opportunity: Dict):
    """Execute arbitrage trade"""
    if not opportunity['is_viable']:
        st.error(f"❌ Trade not viable! Net profit: {opportunity['net_profit_pct']}%")
        return
    
    # Add to history
    trade = {
        **opportunity,
        'executed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'success'
    }
    st.session_state.trade_history.insert(0, trade)
    st.session_state.total_profit += opportunity['net_profit_usd']
    
    st.success(f"✅ Trade executed successfully! Profit: ${opportunity['net_profit_usd']}")

# Header
st.markdown('<p class="main-header">⚡ Multi-Chain DEX Arbitrage Bot</p>', unsafe_allow_html=True)
st.markdown("**Real-time cross-chain arbitrage scanner across BSC, Polygon, Arbitrum & Base**")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Bot Settings")
    
    min_profit = st.slider("Min Profit %", 0.5, 5.0, 1.5, 0.1)
    trade_size = st.number_input("Trade Size ($)", 100, 100000, 1000, 100)
    
    st.subheader("Trading Pairs")
    selected_pairs = st.multiselect(
        "Select pairs to monitor",
        TRADING_PAIRS,
        default=TRADING_PAIRS[:4]
    )
    
    st.subheader("Enabled Chains")
    enabled_chains = []
    for chain, config in CHAIN_CONFIG.items():
        if st.checkbox(f"{config['icon']} {config['name']}", value=True, key=f"chain_{chain}"):
            enabled_chains.append(chain)
    
    st.divider()
    
    if st.button("🔄 Start Monitoring" if not st.session_state.monitoring else "⏸️ Stop Monitoring", 
                 use_container_width=True,
                 type="primary"):
        st.session_state.monitoring = not st.session_state.monitoring
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.trade_history = []
        st.session_state.total_profit = 0
        st.rerun()
    
    st.divider()
    st.caption(f"Monitoring: {'🟢 Active' if st.session_state.monitoring else '🔴 Inactive'}")

settings = {
    'min_profit': min_profit,
    'trade_size': trade_size,
    'trading_pairs': selected_pairs,
    'enabled_chains': enabled_chains
}

# Auto-refresh when monitoring
if st.session_state.monitoring:
    st.session_state.opportunities = scan_opportunities(settings)
    st.session_state.chain_stats = calculate_chain_stats(st.session_state.opportunities)
    time.sleep(1)
    st.rerun()

# Main Dashboard
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🎯 Opportunities", "📈 Analytics", "📜 Trade History"])

with tab1:
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Profit", f"${st.session_state.total_profit:.2f}", 
                 delta=f"{len(st.session_state.trade_history)} trades")
    
    with col2:
        viable_count = sum(1 for o in st.session_state.opportunities if o['is_viable'])
        st.metric("🎯 Viable Opportunities", viable_count,
                 delta=f"{len(st.session_state.opportunities)} total")
    
    with col3:
        avg_profit = sum(o['net_profit_pct'] for o in st.session_state.opportunities if o['is_viable'])
        avg_profit = avg_profit / viable_count if viable_count > 0 else 0
        st.metric("📊 Avg Profit", f"{avg_profit:.2f}%")
    
    with col4:
        best_profit = max((o['net_profit_pct'] for o in st.session_state.opportunities if o['is_viable']), default=0)
        st.metric("🚀 Best Opportunity", f"{best_profit:.2f}%")
    
    st.divider()
    
    # Chain Performance Cards
    st.subheader("🔗 Chain Performance")
    cols = st.columns(len(enabled_chains))
    
    for idx, chain in enumerate(enabled_chains):
        with cols[idx]:
            config = CHAIN_CONFIG[chain]
            stats = st.session_state.chain_stats.get(chain, {'total': 0, 'viable': 0, 'avg_profit': 0})
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {config['color']}22, {config['color']}11); 
                        padding: 1rem; border-radius: 10px; border: 2px solid {config['color']};">
                <h3 style="margin: 0;">{config['icon']} {config['name']}</h3>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">
                    <strong>Opportunities:</strong> {stats['viable']}/{stats['total']}<br>
                    <strong>Avg Profit:</strong> <span style="color: #10b981;">{stats['avg_profit']}%</span><br>
                    <strong>Best:</strong> <span style="color: #fbbf24;">{stats['best_profit']}%</span><br>
                    <strong>Gas:</strong> ~${config['avg_gas'] * config['native_price']:.4f}
                </p>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.subheader("🎯 Live Arbitrage Opportunities")
    
    if not st.session_state.monitoring:
        st.info("👆 Click 'Start Monitoring' in the sidebar to scan for opportunities")
    elif not st.session_state.opportunities:
        st.warning("⏳ Scanning for opportunities...")
    else:
        # Filter options
        col1, col2 = st.columns([1, 3])
        with col1:
            show_viable = st.checkbox("Show only viable", value=True)
        with col2:
            chain_filter = st.selectbox("Filter by chain", ["All"] + [CHAIN_CONFIG[c]['name'] for c in enabled_chains])
        
        # Filter opportunities
        filtered_opps = st.session_state.opportunities
        if show_viable:
            filtered_opps = [o for o in filtered_opps if o['is_viable']]
        if chain_filter != "All":
            filtered_opps = [o for o in filtered_opps if o['chain_name'] == chain_filter]
        
        st.write(f"Showing **{len(filtered_opps)}** opportunities")
        
        # Display opportunities
        for idx, opp in enumerate(filtered_opps[:20]):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"""
                **{opp['chain_icon']} {opp['chain_name']} - {opp['pair']}**  
                Buy: {opp['dex1']} @ ${opp['price1']} → Sell: {opp['dex2']} @ ${opp['price2']}
                """)
            
            with col2:
                profit_color = "green" if opp['is_viable'] else "red"
                st.markdown(f"""
                Gross: <span style="color: orange;">+{opp['gross_profit_pct']}%</span> | 
                Gas: <span style="color: red;">-{opp['gas_cost_pct']}%</span>  
                **Net: <span style="color: {profit_color};">{opp['net_profit_pct']}%</span> 
                (${opp['net_profit_usd']})**
                """, unsafe_allow_html=True)
            
            with col3:
                if st.button("Execute", key=f"exec_{idx}", disabled=not opp['is_viable']):
                    execute_trade(opp)
                    st.rerun()
            
            st.divider()

with tab3:
    st.subheader("📈 Analytics & Insights")
    
    if st.session_state.opportunities:
        col1, col2 = st.columns(2)
        
        with col1:
            # Chain comparison chart
            chain_data = []
            for chain in enabled_chains:
                stats = st.session_state.chain_stats.get(chain, {})
                chain_data.append({
                    'Chain': CHAIN_CONFIG[chain]['name'],
                    'Viable Opportunities': stats.get('viable', 0),
                    'Avg Profit (%)': stats.get('avg_profit', 0)
                })
            
            df_chains = pd.DataFrame(chain_data)
            fig1 = px.bar(df_chains, x='Chain', y='Viable Opportunities',
                         title="Viable Opportunities by Chain",
                         color='Avg Profit (%)',
                         color_continuous_scale='RdYlGn')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Profit distribution
            profit_data = [o['net_profit_pct'] for o in st.session_state.opportunities if o['is_viable']]
            if profit_data:
                fig2 = go.Figure(data=[go.Histogram(x=profit_data, nbinsx=20)])
                fig2.update_layout(title="Profit Distribution", xaxis_title="Net Profit %", yaxis_title="Count")
                st.plotly_chart(fig2, use_container_width=True)
        
        # Best opportunities table
        st.subheader("🏆 Top 10 Opportunities")
        top_opps = [o for o in st.session_state.opportunities if o['is_viable']][:10]
        df_top = pd.DataFrame([{
            'Chain': o['chain_icon'] + ' ' + o['chain_name'],
            'Pair': o['pair'],
            'Route': f"{o['dex1']} → {o['dex2']}",
            'Net Profit %': o['net_profit_pct'],
            'Net Profit $': o['net_profit_usd'],
            'Gas Cost $': o['gas_cost_usd']
        } for o in top_opps])
        
        if not df_top.empty:
            st.dataframe(df_top, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("📜 Trade History")
    
    if not st.session_state.trade_history:
        st.info("No trades executed yet. Start monitoring and execute profitable opportunities!")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Trades", len(st.session_state.trade_history))
        with col2:
            avg_trade_profit = st.session_state.total_profit / len(st.session_state.trade_history)
            st.metric("Avg Profit/Trade", f"${avg_trade_profit:.2f}")
        with col3:
            success_rate = 100  # All executed trades are successful in this demo
            st.metric("Success Rate", f"{success_rate}%")
        
        st.divider()
        
        for trade in st.session_state.trade_history[:20]:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"""
                **{trade['chain_icon']} {trade['chain_name']} - {trade['pair']}**  
                {trade['dex1']} → {trade['dex2']} | {trade['executed_at']}
                """)
            
            with col2:
                st.markdown(f"""
                Net Profit: <span style="color: green; font-weight: bold;">{trade['net_profit_pct']}%</span>  
                Amount: <span style="color: green; font-weight: bold;">${trade['net_profit_usd']}</span>
                """, unsafe_allow_html=True)
            
            with col3:
                st.success("✅ Success")
            
            st.divider()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>⚠️ Educational Demo Only</strong></p>
    <p style="font-size: 0.9rem;">
        This is a simulation for learning purposes. Real arbitrage trading requires actual blockchain integration,
        private RPC nodes, gas optimization, MEV protection, and significant capital.
    </p>
    <p style="font-size: 0.8rem; margin-top: 1rem;">
        Built with ❤️ using Streamlit | <a href="https://github.com" target="_blank">View on GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)
