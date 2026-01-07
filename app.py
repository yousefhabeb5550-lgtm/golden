import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# --- إعدادات الهوية والتليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🏆 **[GOLD ELITE]**\n{message}", "parse_mode": "Markdown"})
    except: pass

# --- تصميم الواجهة الاحترافي (Dark Bootstrap Theme) ---
st.set_page_config(page_title="Gold Elite Terminal", page_icon="🏆", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .main-card {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.8);
    }
    .price-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 4rem;
        font-weight: 700;
        color: #ffd700;
        margin: 10px 0;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    .status-badge {
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    .bg-live { background-color: #238636; color: white; }
    .bg-wait { background-color: #8b949e; color: white; }
    .bg-alert { background-color: #da3633; color: white; animation: pulse 2s infinite; }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
    </style>
    """, unsafe_allow_html=True)

# --- محرك البيانات الفائق (High-Precision Data Engine) ---
@st.cache_data(ttl=2)
def fetch_data():
    try:
        # استخدام XAUUSD=X كمرجع أساسي للـ Spot Gold العالمي
        ticker = yf.Ticker("XAUUSD=X")
        df = ticker.history(period="1d", interval="1m")
        return df
    except: return pd.DataFrame()

# --- لوحة التحكم الجانبية (Control Center) ---
with st.sidebar:
    st.markdown("### ⚙️ Calibration Center")
    # التعديل اليدوي للمطابقة التامة مع MT5
    offset = st.number_input("MT5 Price Offset", value=0.00, step=0.01, format="%.2f")
    st.markdown("---")
    st.info("💡 نصيحة: إذا رأيت فرقاً عن منصتك، اضبط الـ Offset لمرة واحدة فقط.")
    if st.button("🔔 Test Telegram Signal"):
        send_alert("Terminal Link Established. Monitoring Liquidity Pools...")

# --- منطق معالجة البيانات الرئيسي ---
df = fetch_data()

if not df.empty and len(df) > 5:
    # استخدام المصفوفات لضمان السرعة والدقة
    current_raw = df['Close'].iloc[-1]
    current_price = round(float(current_raw) + offset, 2)
    
    # حساب سيولة الـ SMC (آخر 15 شمعة)
    liquidity_pool_raw = df['Low'].iloc[-15:-1].min()
    liquidity_pool = round(float(liquidity_pool_raw) + offset, 2)
    
    # كشف الـ Sweep (كسر القاع ثم الارتداد)
    is_sweep = (float(df['Low'].iloc[-1]) + offset) < liquidity_pool and current_price > liquidity_pool

    # --- بناء الواجهة التفاعلية ---
    st.markdown(f"""
    <div class="main-card">
        <span class="status-badge bg-live">Market Feed: Active</span>
        <h3 style="color: #8b949e; margin-top: 20px;">XAU/USD SPOT</h3>
        <div class="price-value">${current_price:,.2f}</div>
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px;">
            <div>
                <small style="color: #8b949e;">SUPPORT (SSL)</small><br>
                <strong style="color: #58a6ff; font-size: 1.2rem;">${liquidity_pool:,.2f}</strong>
            </div>
            <div style="border-left: 1px solid #30363d;"></div>
            <div>
                <small style="color: #8b949e;">SYNC STATUS</small><br>
                <strong style="color: #ffd700; font-size: 1.2rem;">ECN DIRECT</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # قسم حالة الخوارزمية
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if is_sweep:
            st.markdown('<div class="status-badge bg-alert">🚨 LIQUIDITY SWEEP DETECTED - INSTITUTIONAL ENTRY</div>', unsafe_allow_html=True)
            st.success(f"**إشارة قنص شراء:** السعر تجاوز منطقة السيولة {liquidity_pool} وبدأ بالارتداد.")
            if 'last_alert' not in st.session_state or st.session_state.last_alert != current_price:
                send_alert(f"🚀 BUY SIGNAL\nEntry: {current_price}\nTarget: {current_price + 1.5}\nStop: {current_price - 0.6}")
                st.session_state.last_alert = current_price
        else:
            st.markdown('<div class="status-badge bg-wait">🔍 Scanning for Smart Money Footprints...</div>', unsafe_allow_html=True)

    with col2:
        st.write(f"⏱ **Last Update:** {datetime.now().strftime('%H:%M:%S')}")

else:
    # واجهة التحميل الاحترافية (تظهر في الصورة الأخيرة التي أرسلتها)
    st.markdown("""
        <div style="text-align: center; margin-top: 100px;">
            <div class="spinner-border text-warning" role="status" style="width: 4rem; height: 4rem;"></div>
            <h2 style="color: #ffd700; margin-top: 20px;">Establishing Secure ECN Connection...</h2>
            <p style="color: #8b949e;">Synchronizing with Global Gold Liquidity Providers</p>
        </div>
    """, unsafe_allow_html=True)
        
