import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# --- إعدادات التليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_gorilla_alert(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🦍 **[GORILLA EUR/USD]**\n{msg}", "parse_mode": "Markdown"})
    except: pass

# --- واجهة المستخدم الاحترافية (Bootstrap Style) ---
st.set_page_config(page_title="Euro Gorilla Sniper", page_icon="🦍", layout="wide")

st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0b0e14 !important; color: #ffffff; }
        .stApp { background-color: #0b0e14; }
        .gorilla-card { 
            background: linear-gradient(145deg, #161b22, #0d1117); 
            border: 1px solid #30363d; border-radius: 15px; 
            padding: 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .price-big { font-family: 'JetBrains Mono', monospace; font-size: 5rem; font-weight: 800; color: #00ff88; }
        .status-badge { padding: 5px 15px; border-radius: 50px; font-size: 0.8rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- محرك البحث عن الفرص (SMC Core) ---
def analyze_market():
    # سحب بيانات اليورو (ECN Feed)
    df = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
    if df.empty or len(df) < 20: return None, False, 0
    
    # 1. تحديد السيولة (قاع آخر 15 دقيقة)
    ssl = float(df['Low'].iloc[-15:-1].min())
    current_close = float(df['Close'].iloc[-1])
    current_low = float(df['Low'].iloc[-1])
    
    # 2. كشف الفجوة السعرية FVG (الاندفاع المؤسسي)
    # نقارن شمعة ما قبل السابقة مع الشمعة الحالية
    prev_high = float(df['High'].iloc[-3])
    curr_low = float(df['Low'].iloc[-1])
    fvg_detected = curr_low > prev_high # فجوة شرائية صاعدة
    
    # 3. شرط دخول الغوريلا
    # سحب سيولة (ذيل شمعة تحت القاع) + إغلاق فوق القاع + وجود فجوة FVG
    is_setup = current_low < ssl and current_close > ssl and fvg_detected
    
    return round(current_close, 5), is_setup, round(ssl, 5)

# --- العرض الرئيسي ---
price, setup, liquidity_level = analyze_market()

st.markdown(f"""
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-10">
                <div class="gorilla-card">
                    <span class="status-badge bg-primary text-white mb-3">SMC GORILLA ENGINE ACTIVE</span>
                    <h5 class="text-muted">EUR/USD LIVE PRICE</h5>
                    <div class="price-big">{price if price else "---"}</div>
                    <div class="row mt-4">
                        <div class="col-6 border-end border-secondary">
                            <small class="text-muted">LIQUIDITY TARGET (SSL)</small>
                            <h3 class="text-info">{liquidity_level}</h3>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">MARKET STRUCTURE</small>
                            <h3 class="text-warning">SCANNING...</h3>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# نظام التنبيهات
if setup:
    st.balloons()
    st.success("🔥 GORILLA ALERT: Liquidity Swept + FVG Confirmed!")
    send_gorilla_alert(f"🚀 فرصة قنص يورو!\nالسعر: {price}\nالسيولة المسحوبة: {liquidity_level}\nالنوع: SMC Bullish Reversal")

# تحديث تلقائي كل 10 ثوانٍ
time.sleep(10)
st.rerun()
