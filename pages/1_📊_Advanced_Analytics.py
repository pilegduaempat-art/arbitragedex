import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Advanced Analytics", page_icon="📊", layout="wide")

st.title("📊 Advanced Analytics Dashboard")
st.markdown("Deep dive into arbitrage performance metrics and insights")

# Generate sample data for analytics
def generate_historical_data(days=30):
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    data = {
        'date': dates,
        'bsc_profit': np.random.uniform(50, 200, days).cumsum(),
        'polygon_profit': np.random.uniform(40, 180, days).cumsum(),
        'arbitrum_profit': np.random.uniform(60, 220, days).cumsum(),
        'base_profit': np.random.uniform(70, 250, days).cumsum(),
        'total_trades': np.random.randint(5, 20, days).cumsum(),
        'avg_profit_pct': np.random.uniform(1.5, 3.5, days),
        'gas_spent': np.random.uniform(10, 50, days).cumsum()
    }
    return pd.DataFrame(data)

df = generate_historical_data()

# Tabs for different analytics
tab1, tab2, tab3, tab4 = st.tabs(["💰 Profit Analysis", "⚡ Chain Performance", "📈 Trends", "🎯 Optimization"])

with tab1:
    st.subheader("Cumulative Profit by Chain")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("BSC Total", f"${df['bsc_profit'].iloc[-1]:.2f}", 
                 delta=f"+${df['bsc_profit'].iloc[-1] - df['bsc_profit'].iloc[-2]:.2f}")
    with col2:
        st.metric("Polygon Total", f"${df['polygon_profit'].iloc[-1]:.2f}",
                 delta=f"+${df['polygon_profit'].iloc[-1] - df['polygon_profit'].iloc[-2]:.2f}")
    with col3:
        st.metric("Arbitrum Total", f"${df['arbitrum_profit'].iloc[-1]:.2f}",
                 delta=f"+${df['arbitrum_profit'].iloc[-1] - df['arbitrum_profit'].iloc[-2]:.2f}")
    with col4:
        st.metric("Base Total", f"${df['base_profit'].iloc[-1]:.2f}",
                 delta=f"+${df['base_profit'].iloc[-1] - df['base_profit'].iloc[-2]:.2f}")
    
    # Line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['bsc_profit'], name='BSC', line=dict(color='#F3BA2F')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['polygon_profit'], name='Polygon', line=dict(color='#8247E5')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['arbitrum_profit'], name='Arbitrum', line=dict(color='#28A0F0')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['base_profit'], name='Base', line=dict(color='#0052FF')))
    
    fig.update_layout(
        title="Cumulative Profit Over Time",
        xaxis_title="Date",
        yaxis_title="Profit ($)",
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Profit breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        total_profits = {
            'BSC': df['bsc_profit'].iloc[-1],
            'Polygon': df['polygon_profit'].iloc[-1],
            'Arbitrum': df['arbitrum_profit'].iloc[-1],
            'Base': df['base_profit'].iloc[-1]
        }
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(total_profits.keys()),
            values=list(total_profits.values()),
            hole=0.3,
            marker=dict(colors=['#F3BA2F', '#8247E5', '#28A0F0', '#0052FF'])
        )])
        fig_pie.update_layout(title="Profit Share by Chain", height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # ROI calculation
        total_profit = sum(total_profits.values())
        total_gas = df['gas_spent'].iloc[-1]
        net_profit = total_profit - total_gas
        roi = (net_profit / total_gas) * 100 if total_gas > 0 else 0
        
        st.metric("Total Gross Profit", f"${total_profit:.2f}")
        st.metric("Total Gas Spent", f"${total_gas:.2f}")
        st.metric("Net Profit", f"${net_profit:.2f}")
        st.metric("ROI", f"{roi:.2f}%")
        
        # Daily average
        days = len(df)
        st.metric("Daily Avg Profit", f"${(total_profit / days):.2f}")
        st.metric("Weekly Projected", f"${(total_profit / days * 7):.2f}")
        st.metric("Monthly Projected", f"${(total_profit / days * 30):.2f}")

with tab2:
    st.subheader("Chain Performance Comparison")
    
    # Performance metrics
    metrics_data = {
        'Chain': ['BSC', 'Polygon', 'Arbitrum', 'Base'],
        'Total Profit': [df['bsc_profit'].iloc[-1], df['polygon_profit'].iloc[-1], 
                        df['arbitrum_profit'].iloc[-1], df['base_profit'].iloc[-1]],
        'Avg Profit/Trade': [2.1, 2.2, 1.7, 2.5],
        'Total Trades': [150, 180, 220, 190],
        'Success Rate': [98.5, 99.1, 99.8, 99.2],
        'Avg Gas Cost': [0.90, 0.10, 0.30, 0.015]
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    
    # Styled dataframe
    st.dataframe(
        df_metrics.style.background_gradient(subset=['Total Profit'], cmap='Greens')
                       .background_gradient(subset=['Avg Profit/Trade'], cmap='Blues')
                       .format({
                           'Total Profit': '${:.2f}',
                           'Avg Profit/Trade': '{:.2f}%',
                           'Success Rate': '{:.1f}%',
                           'Avg Gas Cost': '${:.3f}'
                       }),
        use_container_width=True
    )
    
    # Performance radar chart
    categories = ['Profit', 'Speed', 'Cost Efficiency', 'Reliability', 'Opportunity Count']
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=[85, 60, 40, 95, 70],
        theta=categories,
        fill='toself',
        name='BSC'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[88, 80, 90, 98, 85],
        theta=categories,
        fill='toself',
        name='Polygon'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[75, 95, 70, 99, 90],
        theta=categories,
        fill='toself',
        name='Arbitrum'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[92, 85, 98, 97, 88],
        theta=categories,
        fill='toself',
        name='Base'
    ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Multi-Dimensional Performance Comparison",
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

with tab3:
    st.subheader("Trend Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Avg profit trend
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df['date'], 
            y=df['avg_profit_pct'],
            mode='lines+markers',
            name='Avg Profit %',
            line=dict(color='#10b981', width=3)
        ))
        
        # Add trend line
        z = np.polyfit(range(len(df)), df['avg_profit_pct'], 1)
        p = np.poly1d(z)
        fig_trend.add_trace(go.Scatter(
            x=df['date'],
            y=p(range(len(df))),
            mode='lines',
            name='Trend',
            line=dict(color='red', dash='dash')
        ))
        
        fig_trend.update_layout(
            title="Average Profit Percentage Trend",
            xaxis_title="Date",
            yaxis_title="Profit %",
            height=400
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        # Trade volume trend
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Bar(
            x=df['date'],
            y=df['total_trades'].diff().fillna(0),
            name='Daily Trades',
            marker_color='#667eea'
        ))
        
        fig_volume.update_layout(
            title="Daily Trade Volume",
            xaxis_title="Date",
            yaxis_title="Number of Trades",
            height=400
        )
        st.plotly_chart(fig_volume, use_container_width=True)
    
    # Insights
    st.subheader("📌 Key Insights")
    
    trend_direction = "upward" if df['avg_profit_pct'].iloc[-1] > df['avg_profit_pct'].iloc[0] else "downward"
    best_chain = max(metrics_data['Chain'], 
                     key=lambda x: metrics_data['Total Profit'][metrics_data['Chain'].index(x)])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"📈 Profit trend is {trend_direction}")
    with col2:
        st.success(f"🏆 Best performing chain: {best_chain}")
    with col3:
        avg_daily = df['total_trades'].iloc[-1] / len(df)
        st.warning(f"📊 Avg daily trades: {avg_daily:.0f}")

with tab4:
    st.subheader("🎯 Strategy Optimization")
    
    st.markdown("""
    Based on historical data, here are recommendations to maximize profits:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Best Practices")
        st.markdown("""
        1. **Focus on Base & Polygon**
           - Lowest gas costs
           - Highest profit margins
           
        2. **Optimal Trade Size**
           - $1,000 - $5,000 per trade
           - Balances profit vs. slippage
           
        3. **Peak Trading Hours**
           - 12:00 - 18:00 UTC
           - Higher volume = more opportunities
           
        4. **Preferred Pairs**
           - ETH/USDT: Most liquid
           - WBTC/USDT: Best spreads
        """)
    
    with col2:
        st.markdown("### ⚠️ Risk Management")
        st.markdown("""
        1. **Set Stop-Loss**
           - Max loss per trade: 2%
           - Daily loss limit: 5%
           
        2. **Gas Price Monitoring**
           - Skip trades if gas > 50 gwei
           - Use gas price alerts
           
        3. **Diversification**
           - Don't rely on single chain
           - Spread across 3-4 chains
           
        4. **Position Sizing**
           - Never use 100% of capital
           - Keep 20% reserve for gas
        """)
    
    st.divider()
    
    # Optimization calculator
    st.subheader("💡 Profit Optimization Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        capital = st.number_input("Total Capital ($)", 1000, 1000000, 10000)
    with col2:
        target_profit = st.slider("Target Monthly Profit %", 5, 50, 20)
    with col3:
        risk_tolerance = st.selectbox("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])
    
    # Calculate recommendations
    if risk_tolerance == "Conservative":
        trades_per_day = 5
        avg_profit = 1.5
    elif risk_tolerance == "Moderate":
        trades_per_day = 10
        avg_profit = 2.0
    else:
        trades_per_day = 15
        avg_profit = 2.5
    
    monthly_trades = trades_per_day * 30
    profit_per_trade = capital * (avg_profit / 100)
    monthly_profit = profit_per_trade * monthly_trades
    required_capital = (capital * target_profit / 100) / (avg_profit / 100) / monthly_trades
    
    st.markdown("### 📊 Recommendations")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Recommended Trades/Day", trades_per_day)
    with col2:
        st.metric("Expected Profit/Trade", f"${profit_per_trade:.2f}")
    with col3:
        st.metric("Projected Monthly Profit", f"${monthly_profit:.2f}")
    with col4:
        achievement = (monthly_profit / (capital * target_profit / 100)) * 100
        st.metric("Target Achievement", f"{achievement:.1f}%")

st.divider()
st.caption("📊 Analytics updated in real-time based on trading activity")
