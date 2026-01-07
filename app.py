import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# --- إعدادات التليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_gorilla_alert(pair, price, msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        text = f"🦍 **[GORILLA ALERT: {pair}]**\n💰 Price: {price}\n📝 Status: {msg}"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except: pass

# --- دالة حساب RSI احترافية آمنة ---
def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- إعدادات الواجهة (Dark Gorilla Theme) ---
st.set_page_config(page_title="Gorilla Multi-Radar Pro", page_icon="🦍", layout="wide")

st.markdown("""
    <style>
    body { background-color: #0b0e14 !important; color: white; }
    .stApp { background-color: #0b0e14; }
    .pair-card { 
        background: #161b22; border: 1px solid #30363d; border-radius: 12px; 
        padding: 20px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .price-tag { font-family: 'JetBrains Mono', monospace; font-size: 3rem; color: #00ff88; font-weight: bold; }
    .rsi-container { margin-top: 15px; }
    .rsi-badge { padding: 4px 12px; border-radius: 8px; font-weight: bold; font-size: 0.9rem; background: #0d1117; }
    .label { color: #8b949e; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية (Sidebar) مع زر الاختبار ---
with st.sidebar:
    st.title("🦍 Gorilla Control")
    st.write("---")
    if st.button("🚀 اختبار إرسال تليجرام"):
        send_gorilla_alert("SYSTEM", "LIVE", "✅ زر الاختبار يعمل بنجاح! الرادار يراقب اليورو والباوند الآن.")
        st.success("تم إرسال رسالة الاختبار!")
    st.write("---")
    st.info("الرادار يعمل بنظام التحديث التلقائي لملاحقة السيولة و FVG.")

# --- محرك التحليل الذكي ---
def analyze_pair(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False)
        if df.empty or len(df) < 20: return None
        
        # حساب RSI ومعالجة القيم
        rsi_series = calculate_rsi(df['Close'])
        current_rsi = 50.0
        if not rsi_series.empty and not pd.isna(rsi_series.iloc[-1]):
            current_rsi = round(float(rsi_series.iloc[-1]), 2)
        
        ssl = float(df['Low'].iloc[-20:-1].min())
        current_low = float(df['Low'].iloc[-1])
        current_close = float(df['Close'].iloc[-1])
        
        # FVG Detection
        prev_high = float(df['High'].iloc[-3])
        curr_low = float(df['Low'].iloc[-1])
        fvg_detected = curr_low > prev_high
        
        is_setup = current_low < ssl and current_close > ssl and fvg_detected
        
        return {"price": round(current_close, 5), "ssl": round(ssl, 5), "rsi": current_rsi, "setup": is_setup}
    except: return None

# --- العرض الرئيسي ---
col1, col2 = st.columns(2)
pairs = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X"}

for col, (name, sym) in zip([col1, col2], pairs.items()):
    with col:
        res = analyze_pair(sym)
        if res:
            # تلوين RSI بناءً على الحالة
            rsi_color = "#ff4b4b" if res['rsi'] > 70 else ("#00ff88" if res['rsi'] < 30 else "#8b949e")
            st.markdown(f"""
            <div class="pair-card">
                <div class="label">{name}</div>
                <div class="price-tag">{res['price']}</div>
                <div class="rsi-container">
                    <span class="label">RSI (14):</span> 
                    <span class="rsi-badge" style="color: {rsi_color};">{res['rsi']}</span>
                </div>
                <hr style="border-color: #30363d;">
                <div class="row">
                    <div class="col-6"><small class="label">Liquidity</small><br><b>{res['ssl']}</b></div>
                    <div class="col-6"><small class="label">Status</small><br><b style="color: {'#00ff88' if res['setup'] else '#8b949e'}">{'ENTRY!' if res['setup'] else 'Scanning'}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if res['setup']: send_gorilla_alert(name, res['price'], "Sweep + FVG Confirmed! 🚀")

# التحديث التلقائي
time.sleep(15)
st.rerun()
