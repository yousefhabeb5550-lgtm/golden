import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import time

# --- 1. الإعدادات الأساسية ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🏆 **[GOLD ELITE]**\n{message}", "parse_mode": "Markdown"})
    except: pass

# --- 2. تصميم الواجهة الاحترافية (Custom CSS) ---
st.set_page_config(page_title="Gold Elite Terminal", page_icon="🏆", layout="wide")

st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0b0e14 !important; color: #e0e0e0 !important; }
        .stApp { background-color: #0b0e14; }
        .main-card { background: #161b22; border: 1px solid #30363d; border-radius: 15px; padding: 25px; margin-bottom: 20px; transition: 0.3s; }
        .price-text { font-size: 3rem; font-weight: 800; color: #ffd700; text-shadow: 0 0 15px rgba(255, 215, 0, 0.3); }
        .indicator-badge { border-radius: 50px; padding: 5px 15px; font-size: 0.8rem; font-weight: bold; }
        .bg-gold { background-color: #ffd700; color: #000; }
        .bg-danger-custom { background-color: #ff4b4b; color: #fff; }
        .sidebar-content { background: #161b22; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. محرك البيانات (Data Engine) ---
@st.cache_data(ttl=2)
def get_mt5_compatible_data():
    try:
        # الرمز XAUUSD=X هو المرجعية السعرية لسيولة بنوك Saxo و LMAX المعتمدة في MT5
        ticker = yf.Ticker("XAUUSD=X")
        df = ticker.history(period="1d", interval="1m")
        return df
    except: return pd.DataFrame()

# --- 4. لوحة التحكم الجانبية ---
with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.title("⚙️ Terminal Settings")
    price_offset = st.number_input("MT5 Price Calibration (Offset)", value=0.00, step=0.01, format="%.2f")
    st.markdown("---")
    st.write("📊 **Connectivity:** High-Speed ECN")
    st.write("🕒 **Last Sync:** " + datetime.now().strftime("%H:%M:%S"))
    if st.button("🚀 Force Telegram Ping"):
        send_alert("System calibrated and ready for sniping.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. المعالجة والواجهة الرئيسية ---
df = get_mt5_compatible_data()

if not df.empty and len(df) > 10:
    # استخراج القيم الفردية لضمان عدم حدوث ValueError
    current_raw = float(df['Close'].iloc[-1])
    current_price = round(current_raw + price_offset, 2)
    
    lows_window = df['Low'].iloc[-20:-1]
    raw_liquidity = float(lows_window.min())
    synced_liquidity = round(raw_liquidity + price_offset, 2)
    
    # حساب سحب السيولة (SMC Sweep)
    is_sweep = (float(df['Low'].iloc[-1]) + price_offset) < synced_liquidity and current_price > synced_liquidity

    # --- توزيع Grid يشبه Bootstrap ---
    st.markdown(f"""
        <div class="container-fluid mt-4">
            <div class="row">
                <div class="col-md-8">
                    <div class="main-card shadow">
                        <span class="indicator-badge bg-gold mb-2">LIVE FEED</span>
                        <h1 class="display-6">XAU/USD Spot Price</h1>
                        <div class="price-text">${current_price:,.2f}</div>
                        <p class="text-muted">Real-time sync with global liquidity providers.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="main-card shadow h-100">
                        <span class="indicator-badge bg-info mb-2 text-white">SMC MONITOR</span>
                        <h4>Market Liquidity</h4>
                        <div class="mt-4">
                            <p class="mb-1">Institutional Support (SSL):</p>
                            <h3 class="text-info">${synced_liquidity:,.2f}</h3>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="main-card shadow border-top-gold" style="border-top: 4px solid #ffd700 !important;">
                        <div class="row align-items-center">
                            <div class="col-md-9">
                                <h3>Smart Money Status</h3>
                                <p class="lead">{'🚨 LIQUIDITY PURGE IN PROGRESS - PREPARE TO ENTER' if is_sweep else '🔍 Monitoring for Judas Swing below current support...'}</p>
                            </div>
                            <div class="col-md-3 text-end">
                                <span class="badge {'bg-success' if not is_sweep else 'bg-danger'} p-3 w-100">
                                    {'MARKET STABLE' if not is_sweep else 'ALERT: LIQUIDITY SWEEP'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if is_sweep:
        st.balloons()
        send_alert(f"🚀 BUY SIGNAL\nEntry: {current_price}\nStop: {current_price - 0.5}\nTarget: {current_price + 1.5}")

else:
    st.markdown("""
        <div class="d-flex justify-content-center align-items-center" style="height: 80vh;">
            <div class="spinner-border text-warning" role="status" style="width: 3rem; height: 3rem;"></div>
            <h3 class="ms-3 text-warning">Establishing Secure Connection to ECN Feeds...</h3>
        </div>
    """, unsafe_allow_html=True)
    
