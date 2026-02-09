import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- PAGE CONFIGURATION (Pro Mode) ---
st.set_page_config(
    page_title="Velociraptor: Currency Arbitrage Engine", 
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (For that "Hacker" look) ---
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #30333d;
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .stSuccess { color: #00ff41 !important; }
    .stError { color: #ff2b2b !important; }
</style>
""", unsafe_allow_html=True)

# --- THE WATCHLIST (Expanded for Volatility) ---
# We look for currencies that crash often (High Volatility) or are major hubs.
currencies = {
    "🇯🇵 JPY (Japan)": "JPYINR=X",
    "🇹🇷 TRY (Turkey)": "TRYINR=X",
    "🇦🇷 ARS (Argentina)": "ARSINR=X",
    "🇪🇬 EGP (Egypt)": "EGPINR=X",
    "🇮🇩 IDR (Indonesia)": "IDRINR=X",
    "🇻🇳 VND (Vietnam)": "VNDINR=X",
    "🇰🇷 KRW (South Korea)": "KRWINR=X",
    "🇬🇧 GBP (UK)": "GBPINR=X",
    "🇪🇺 EUR (Europe)": "EURINR=X",
    "🇨🇦 CAD (Canada)": "CADINR=X",
    "🇦🇺 AUD (Australia)": "AUDINR=X",
    "🇦🇪 AED (Dubai)": "AEDINR=X",
    "🇹🇭 THB (Thailand)": "THBINR=X",
    "🇧🇷 BRL (Brazil)": "BRLINR=X",
    "🇿🇦 ZAR (South Africa)": "ZARINR=X",
    "🇳🇴 NOK (Norway)": "NOKINR=X",
}

# --- ENGINE: FETCH DATA ---
@st.cache_data(ttl=300)
def get_market_data():
    data = []
    # Bulk fetch for speed
    tickers = " ".join(currencies.values())
    history = yf.download(tickers, period="30d", interval="1d", progress=False)['Close']
    
    for name, ticker in currencies.items():
        try:
            # Handle Single vs Multi-index columns from yfinance
            if isinstance(history, pd.DataFrame) and ticker in history.columns:
                series = history[ticker]
            elif isinstance(history, pd.Series): # Fallback if only 1 currency requested
                series = history
            else:
                continue

            current_price = float(series.iloc[-1])
            avg_price = float(series.mean())
            
            # THE ARBITRAGE MATH
            # Negative % means the currency is weak (Good for you)
            change_pct = ((current_price - avg_price) / avg_price) * 100
            
            # Recommendation Logic
            signal = "⚪ Neutral"
            impact = "Normal"
            
            if change_pct < -2.0:
                signal = "🟢 BUY SIGNAL (Crash)"
                impact = "High Savings"
            elif change_pct < -0.5:
                signal = "🟡 Discounted"
                impact = "Small Savings"
            elif change_pct > 1.0:
                signal = "🔴 Avoid (Expensive)"
                impact = "Loss"

            data.append({
                "Currency": name,
                "Rate (₹)": current_price,
                "30d Avg": avg_price,
                "Deviation %": change_pct,
                "Signal": signal,
                "Ticker": ticker # Hidden column for calculator
            })
        except Exception as e:
            continue
            
    return pd.DataFrame(data)

# --- APP LAYOUT ---
st.title("✈️ Global Flight Arbitrage Scanner")
st.markdown("Track currencies that are **crashing** against the INR. If a currency is red/weak, change your payment currency to save money.")

col1, col2 = st.columns([2, 1])

# --- LEFT COLUMN: LIVE SCANNER ---
with col1:
    if st.button("🔄 Scan Market Now"):
        st.cache_data.clear()
    
    df = get_market_data()
    
    # Sort by the biggest drop (Best opportunities first)
    df_sorted = df.sort_values(by="Deviation %", ascending=True)
    
    st.dataframe(
        df_sorted[["Currency", "Rate (₹)", "Signal", "Deviation %"]],
        column_config={
            "Deviation %": st.column_config.ProgressColumn(
                "Arbitrage Gap",
                format="%.2f%%",
                min_value=-5,
                max_value=5,
            ),
            "Rate (₹)": st.column_config.NumberColumn(format="%.4f")
        },
        use_container_width=True,
        hide_index=True,
        height=500
    )

# --- RIGHT COLUMN: THE CALCULATOR ---
with col2:
    st.header("🧮 Profit Calculator")
    st.markdown("Found a cheap flight in **Yen** or **Lira**? Check the real cost here.")
    
    # User inputs
    selected_currency_row = st.selectbox("Select Currency:", df_sorted["Currency"])
    
    # Get rate for selected
    rate = df_sorted[df_sorted["Currency"] == selected_currency_row]["Rate (₹)"].values[0]
    
    foreign_price = st.number_input(f"Price in Foreign Currency (e.g. 10,000):", min_value=1.0, value=100.0, step=100.0)
    
    # Calculation
    real_cost_inr = foreign_price * rate
    
    # Bank Fee buffer (approx 2% for forex cards)
    bank_fee = real_cost_inr * 0.02
    total_cost = real_cost_inr + bank_fee
    
    st.divider()
    
    st.metric(label="Real Cost in INR (Market Rate)", value=f"₹ {real_cost_inr:,.2f}")
    st.caption(f"Exchange Rate used: {rate:.4f}")
    
    st.warning(f"⚠️ Est. Cost with 2% Bank Fee: **₹ {total_cost:,.2f}**")
    
    st.markdown("""
    **Strategy:**
    1. Go to Skyscanner/Google Flights.
    2. Change currency (Top Right) to **the one selected above**.
    3. If the price shown there is lower than `₹ {total_cost}`, **BOOK IT!**
    """)

# --- BOTTOM: VISUAL TRENDS ---
st.divider()
st.subheader("📉 Market Volatility Map (Lower is Better)")
fig = px.bar(
    df_sorted,
    x="Currency",
    y="Deviation %",
    color="Deviation %",
    color_continuous_scale=["green", "grey", "red"],
    text_auto='.2s'
)
st.plotly_chart(fig, use_container_width=True)
