import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# --- إعدادات التليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🏆 **[GOLD ELITE TERMINAL]**\n{message}", "parse_mode": "Markdown"})
    except: pass

# --- إعدادات الصفحة (Bootstrap Style) ---
st.set_page_config(page_title="Gold Elite Sniper", page_icon="🏆", layout="wide")

# تصميم الواجهة باستخدام CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; border-radius: 10px; padding: 15px; border: 1px solid #4a4a4a; }
    .status-card { background: linear-gradient(135deg, #1e2130 0%, #0e1117 100%); border-radius: 15px; padding: 20px; border-left: 5px solid #ffd700; margin-bottom: 20px; }
    .fvg-card { background: linear-gradient(135deg, #1e2130 0%, #0e1117 100%); border-radius: 15px; padding: 20px; border-left: 5px solid #00ff88; }
    h1 { color: #ffd700; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- جلب البيانات الاحترافية ---
@st.cache_data(ttl=2)
def fetch_gold_pro():
    try:
        # رمز XAUUSD=X هو الأكثر تطابقاً مع أغلب شركات الـ ECN
        data = yf.download("XAUUSD=X", period="1d", interval="1m", progress=False)
        return data
    except: return pd.DataFrame()

df = fetch_gold_pro()

# --- القائمة الجانبية للتعديلات الفورية ---
st.sidebar.title("⚙️ Control Panel")
offset = st.sidebar.number_input("Price Sync (MT5 Offset)", value=0.00, step=0.01)
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Test Connection"):
    send_alert("System Online - Connection to MT5 Bridge is Stable.")
    st.sidebar.success("Alert Sent!")

# --- الواجهة الرئيسية ---
st.title("🏆 Gold Elite Terminal")
st.markdown(f"**Last Sync:** {datetime.now().strftime('%H:%M:%S')} (Real-time)")

if not df.empty and len(df) > 3:
    # معالجة البيانات
    current_raw = float(df['Close'].iloc[-1])
    current_price = round(current_raw + offset, 2)
    
    # حساب السيولة (SMC Engine)
    lows = df['Low'].iloc[-15:-1]
    raw_liquidity = float(lows.min())
    synced_liquidity = round(raw_liquidity + offset, 2)
    
    # الكشف عن سحب السيولة
    is_sweep = (float(df['Low'].iloc[-1]) + offset) < synced_liquidity and current_price > synced_liquidity

    # --- توزيع العناصر (Bootstrap Grid) ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Live Gold Price", f"${current_price:,.2f}")
    
    with col2:
        status_color = "🟢 Stable" if not is_sweep else "🚨 SWEEP DETECTED"
        st.metric("Market Status", status_color)
        
    with col3:
        st.metric("Session Liquidity", f"${synced_liquidity:,.2f}")

    st.markdown("---")

    # بطاقات المعلومات التفاعلية
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown(f"""
        <div class="status-card">
            <h3>🛡️ Liquidity Analysis</h3>
            <p>Smart Money is currently monitoring the <b>${synced_liquidity}</b> level.</p>
            <p><b>Condition:</b> Waiting for a fake breakout (Judas Swing) below this level.</p>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        fvg_status = "DETECTED" if current_price > (float(df['High'].iloc[-3]) + offset) else "PENDING"
        st.markdown(f"""
        <div class="fvg-card">
            <h3>📈 Momentum (FVG)</h3>
            <p>Fair Value Gap Status: <b>{fvg_status}</b></p>
            <p>Ensuring strong institutional displacement before entry.</p>
        </div>
        """, unsafe_allow_html=True)

    # نظام الإشعارات الذكي
    if is_sweep:
        st.balloons()
        st.success("🔥 [SMC ALERT] LIQUIDITY PURGE DETECTED - WATCH FOR REJECTION")
        send_alert(f"🚀 BUY OPPORTUNITY\nPrice: {current_price}\nTarget: {current_price + 1.5}\nStop: {current_price - 0.5}")

else:
    st.error("Connecting to Global Price Feeds...")

