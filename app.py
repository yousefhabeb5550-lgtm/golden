import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time
import pandas_ta as ta

# --- إعدادات التليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_gorilla_alert(pair, price, msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        text = f"🦍 **[GORILLA ALERT: {pair}]**\n💰 السعر: {price}\n📝 الحالة: {msg}"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except: pass

# --- واجهة المستخدم (Bootstrap Grid) ---
st.set_page_config(page_title="Gorilla Pro Radar", page_icon="🦍", layout="wide")

st.markdown("""
    <style>
    body { background-color: #0b0e14 !important; color: white; }
    .stApp { background-color: #0b0e14; }
    .pair-card { 
        background: #161b22; border: 1px solid #30363d; border-radius: 12px; 
        padding: 20px; text-align: center; margin-bottom: 20px;
    }
    .price-tag { font-family: 'JetBrains Mono', monospace; font-size: 2.8rem; color: #00ff88; font-weight: bold; }
    .rsi-box { font-size: 0.9rem; color: #8b949e; margin-top: 10px; padding: 5px; border-radius: 8px; background: #0d1117; display: inline-block; }
    .label { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
    </style>
""", unsafe_allow_html=True)

# --- إضافة زر الاختبار في القائمة الجانبية ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/614/614568.png", width=100)
    st.title("Gorilla Control")
    st.write("---")
    if st.button("🚀 اختبار إرسال تليجرام"):
        send_gorilla_alert("SYSTEM", "TEST", "✅ زر الاختبار يعمل! الرادار يراقب السوق الآن.")
        st.success("تم إرسال رسالة الاختبار!")
    st.write("---")
    st.info("الرادار يعمل بنظام التحديث التلقائي لملاحقة السيولة و FVG.")

# --- محرك التحليل الفني (SMC + RSI) ---
def analyze_pair(symbol):
    df = yf.download(symbol, period="1d", interval="1m", progress=False)
    if df.empty or len(df) < 30: return None
    
    # 1. حساب RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)
    current_rsi = round(df['RSI'].iloc[-1], 2)
    
    # 2. تحديد السيولة (SSL)
    ssl = float(df['Low'].iloc[-20:-1].min())
    current_low = float(df['Low'].iloc[-1])
    current_close = float(df['Close'].iloc[-1])
    
    # 3. كشف الـ FVG
    prev_high = float(df['High'].iloc[-3])
    curr_low = float(df['Low'].iloc[-1])
    fvg_detected = curr_low > prev_high
    
    # 4. شرط الغوريلا
    is_setup = current_low < ssl and current_close > ssl and fvg_detected
    
    return {
        "price": round(current_close, 5),
        "ssl": round(ssl, 5),
        "rsi": current_rsi,
        "setup": is_setup
    }

# --- العرض الرئيسي ---
col1, col2 = st.columns(2)
pairs = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X"}

with col1:
    res = analyze_pair(pairs["EUR/USD"])
    if res:
        # تحديد لون الـ RSI
        rsi_color = "#ff4b4b" if res['rsi'] > 70 else ("#00ff88" if res['rsi'] < 30 else "#8b949e")
        st.markdown(f"""
        <div class="pair-card">
            <div class="label">EUR / USD</div>
            <div class="price-tag">{res['price']}</div>
            <div class="rsi-box">RSI (14): <span style="color: {rsi_color}; font-weight: bold;">{res['rsi']}</span></div>
            <hr style="border-color: #30363d;">
            <div class="row">
                <div class="col-6"><small class="label">Liquidity</small><br><b>{res['ssl']}</b></div>
                <div class="col-6"><small class="label">SMC Status</small><br><b style="color: {'#00ff88' if res['setup'] else '#8b949e'}">{'ENTRY!' if res['setup'] else 'Scanning'}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if res['setup']: send_gorilla_alert("EUR/USD", res['price'], "Sweep + FVG Confirmed! 🚀")

with col2:
    res = analyze_pair(pairs["GBP/USD"])
    if res:
        rsi_color = "#ff4b4b" if res['rsi'] > 70 else ("#00ff88" if res['rsi'] < 30 else "#8b949e")
        st.markdown(f"""
        <div class="pair-card">
            <div class="label">GBP / USD</div>
            <div class="price-tag" style="color: #58a6ff;">{res['price']}</div>
            <div class="rsi-box">RSI (14): <span style="color: {rsi_color}; font-weight: bold;">{res['rsi']}</span></div>
            <hr style="border-color: #30363d;">
            <div class="row">
                <div class="col-6"><small class="label">Liquidity</small><br><b>{res['ssl']}</b></div>
                <div class="col-6"><small class="label">SMC Status</small><br><b style="color: {'#00ff88' if res['setup'] else '#8b949e'}">{'ENTRY!' if res['setup'] else 'Scanning'}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if res['setup']: send_gorilla_alert("GBP/USD", res['price'], "Sweep + FVG Confirmed! 🚀")

# تحديث تلقائي كل 15 ثانية
time.sleep(15)
st.rerun()
        
