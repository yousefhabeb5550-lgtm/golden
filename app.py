import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# --- إعدادات التليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🦍 [GBP/USD ALERT]\n{msg}"}, timeout=5)
    except: pass

# --- دالة حساب RSI ---
def get_rsi(series, window=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- إعدادات الصفحة ---
st.set_page_config(page_title="GBP/USD Sniper", page_icon="🇬🇧", layout="centered")

st.markdown("""
    <style>
    body { background-color: #0b0e14; color: white; }
    .stApp { background-color: #0b0e14; }
    .main-card { 
        background: #161b22; border: 1px solid #30363d; border-radius: 15px; 
        padding: 30px; text-align: center;
    }
    .price-text { font-family: 'monospace'; font-size: 4rem; color: #58a6ff; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- جلب البيانات بنظام "التنظيف المباشر" ---
try:
    # جلب البيانات مع إلغاء الجداول المتداخلة auto_adjust=True
    data = yf.download("GBPUSD=X", period="1d", interval="1m", progress=False, auto_adjust=True)
    
    if not data.empty and len(data) > 20:
        # تأكيد الحصول على عمود Close بشكل صريح
        df = data.copy()
        current_price = float(df['Close'].iloc[-1])
        ssl_level = float(df['Low'].iloc[-20:-1].min())
        
        rsi_series = get_rsi(df['Close'])
        rsi_val = round(float(rsi_series.iloc[-1]), 2) if not pd.isna(rsi_series.iloc[-1]) else 50.0
        
        is_setup = float(df['Low'].iloc[-1]) < ssl_level and float(df['Close'].iloc[-1]) > ssl_level

        st.markdown(f"""
            <div class="main-card">
                <h2 style="color:#8b949e;">GBP / USD LIVE</h2>
                <div class="price-text">{current_price:.5f}</div>
                <p>RSI: <span style="color:#00ff88">{rsi_val}</span> | SSL: {ssl_level:.5f}</p>
                <h3 style="color: {'#00ff88' if is_setup else '#8b949e'}">
                    {'🚨 ENTRY DETECTED!' if is_setup else '🔍 Scanning Market...'}
                </h3>
            </div>
        """, unsafe_allow_html=True)

        if is_setup:
            send_telegram(f"🚀 فرصة قنص باوند!\nالسعر: {current_price:.5f}")
            st.balloons()
    else:
        st.info("🔄 بانتظار استلام بيانات السعر من السيرفر العالمي...")

except Exception as e:
    st.error("⚠️ جاري إعادة الاتصال بمزود البيانات...")

time.sleep(15)
st.rerun()
