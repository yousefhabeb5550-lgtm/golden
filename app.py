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
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🦍 [GBP/USD] {msg}"}, timeout=5)
    except: pass

st.set_page_config(page_title="GBP/USD Sniper", layout="centered")

st.markdown("""
    <style>
    .main-card { background: #161b22; border-radius: 20px; padding: 40px; text-align: center; border: 2px solid #30363d; }
    .price { font-size: 5rem; color: #58a6ff; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

try:
    # جلب السعر الحالي فقط بطريقة سريعة جداً
    ticker = yf.Ticker("GBPUSD=X")
    data = ticker.history(period="1d", interval="1m")
    
    if not data.empty:
        # تحويل البيانات إلى أرقام بسيطة
        current_price = float(data['Close'].iloc[-1])
        low_price = float(data['Low'].iloc[-20:].min())
        
        st.markdown(f"""
            <div class="main-card">
                <h2 style="color:#8b949e">GBP / USD</h2>
                <div class="price">{current_price:.5f}</div>
                <hr style="border-color:#333">
                <p style="font-size:1.2rem">Low (20m): {low_price:.5f}</p>
                <p style="color:#00ff88">🔍 الرادار يعمل ويبحث عن سحب السيولة...</p>
            </div>
        """, unsafe_allow_html=True)
        
        # شرط بسيط جداً للتأكد من عمل التنبيهات
        if current_price <= low_price:
            send_telegram(f"🚨 السعر لمس أدنى مستوى! {current_price:.5f}")
    else:
        st.error("❌ فشل في قراءة جدول البيانات من Yahoo")

except Exception as e:
    st.warning(f"⚠️ جاري المحاولة مرة أخرى... (تحقق من Reboot السيرفر)")

time.sleep(15)
st.rerun()
