import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="1% Flight Arbitrage Terminal", layout="wide")

st.title("🕵️ Master Currency Loophole Engine (2026 Edition)")
st.markdown("---")

# THE COMPLETE MASTER LIST
currencies = {
    "🇺🇸 USD (USA)": "USDINR=X", "🇬🇧 GBP (UK)": "GBPINR=X", "🇪🇺 EUR (Europe)": "EURINR=X",
    "🇯🇵 JPY (Japan)": "JPYINR=X", "🇹🇷 TRY (Turkey)": "TRYINR=X", "🇦🇷 ARS (Argentina)": "ARSINR=X",
    "🇪🇬 EGP (Egypt)": "EGPINR=X", "🇦🇪 AED (Dubai)": "AEDINR=X", "🇨🇦 CAD (Canada)": "CADINR=X",
    "🇦🇺 AUD (Australia)": "AUDINR=X", "🇧🇷 BRL (Brazil)": "BRLINR=X", "🇿🇦 ZAR (South Africa)": "ZARINR=X",
    "🇻🇳 VND (Vietnam)": "VNDINR=X", "🇳🇴 NOK (Norway)": "NOKINR=X", "🇷🇺 RUB (Russia)": "RUBINR=X",
    "🇮🇩 IDR (Indonesia)": "IDRINR=X", "🇸🇬 SGD (Singapore)": "SGDINR=X", "🇨🇭 CHF (Swiss)": "CHFINR=X"
}

@st.cache_data(ttl=600)
def fetch_elite_data():
    results = []
    for name, ticker in currencies.items():
        try:
            t = yf.Ticker(ticker)
            # Fetch 1y data to calculate the "Arbitrage Gap" (How much it crashed from peak)
            hist = t.history(period="1y")
            if not hist.empty:
                current_rate = hist['Close'].iloc[-1]
                year_high = hist['Close'].max()
                # Arbitrage Gap: If the currency is much cheaper than its 1y high, it's a booking loophole
                gap = ((year_high - current_rate) / year_high) * 100
                
                results.append({
                    "Currency": name,
                    "Live Rate (₹)": round(current_rate, 4),
                    "Arb Gap %": round(gap, 2),
                    "Status": "🟢 LOOPHOLE" if gap > 10 else "⚪ Stable"
                })
        except:
            continue
    return pd.DataFrame(results)

data_load_state = st.info("🔍 Scanning global markets for mispriced currencies...")
df = fetch_elite_data()
data_load_state.empty()

if not df.empty:
    # Sort by the biggest Arbitrage Gap
    df_sorted = df.sort_values(by="Arb Gap %", ascending=False)
    
    # --- TOP DASHBOARD ---
    winner = df_sorted.iloc[0]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🏆 WINNER (Lowest INR Cost)", winner['Currency'], f"{winner['Arb Gap %']}% Cheaper")
    with c2:
        st.metric("🚀 BEST STABLE (USD)", f"₹{df[df['Currency'] == '🇺🇸 USD (USA)']['Live Rate (₹)'].values[0]}")
    with c3:
        st.metric("📉 TOTAL TRACKED", len(df))

    # --- FLIGHT CALCULATOR ---
    st.markdown("### ✈️ Loophole Savings Calculator")
    col_a, col_b = st.columns(2)
    with col_a:
        ticket_price_inr = st.number_input("Estimated Ticket Price in INR (on Indian sites):", value=50000)
        selected_loophole = st.selectbox("Select Booking Currency (VPN Region):", df_sorted["Currency"])
    
    target_rate = df[df["Currency"] == selected_loophole]["Live Rate (₹)"].values[0]
    arb_gap = df[df["Currency"] == selected_loophole]["Arb Gap %"].values[0]
    
    potential_savings = ticket_price_inr * (arb_gap / 100)
    
    with col_b:
        st.warning(f"By booking via **{selected_loophole}** site, you could save approx:")
        st.title(f"₹{potential_savings:,.0f}")
        st.caption(f"Estimated price via loophole: ₹{ticket_price_inr - potential_savings:,.0f}")

    # --- FULL DATA TABLE ---
    st.subheader("📊 Global Arbitrage Opportunity Table")
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)

    # Charting the Loophole
    fig = px.bar(df_sorted, x="Currency", y="Arb Gap %", color="Arb Gap %", 
                 title="Currency Devaluation (Higher = Better Flight Deal)",
                 color_continuous_scale="Greens")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Financial markets are currently throttled. Please refresh in 2 minutes.")

st.sidebar.markdown("""
**1% Strategy Guide:**
1. Find a **🟢 LOOPHOLE** currency.
2. Use a VPN to set your location to that country.
3. Use the airline's **local** website (e.g. .com.tr for Turkey).
4. Pay in the local currency. Your Indian card will convert it at the live rate, saving you the 'India Premium'.
""")
