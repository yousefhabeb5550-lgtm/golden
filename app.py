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
    except:
        pass

# --- دالة حساب RSI آمنة ---
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
        padding: 30px; text-align: center; box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    .price-text { font-family: 'monospace'; font-size: 4rem; color: #58a6ff; font-weight: bold; }
    .status-badge { padding: 5px 15px; border-radius: 50px; background: #21262d; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("🦍 Gorilla Terminal")
    if st.button("🚀 اختبار اتصال التليجرام"):
        send_telegram("✅ البوت متصل ويراقب الباوند دولار الآن!")
        st.success("تم الإرسال!")
    st.write("---")
    st.info("تحديث تلقائي كل 15 ثانية لملاحقة السيولة.")

# --- جلب البيانات والتحليل بنظام حماية ---
try:
    # جلب البيانات
    df = yf.download("GBPUSD=X", period="1d", interval="1m", progress=False)
    
    # التأكد من أن البيانات ليست فارغة وصحيحة برمجياً
    if df is not None and not df.empty and len(df) > 20:
        
        # استخراج القيم الفردية لضمان عدم حدوث خطأ Series
        current_price = float(df['Close'].iloc[-1])
        ssl_level = float(df['Low'].iloc[-20:-1].min())
        
        # حساب RSI
        rsi_series = get_rsi(df['Close'])
        rsi_val = round(float(rsi_series.iloc[-1]), 2) if not pd.isna(rsi_series.iloc[-1]) else 50.0
        
        # منطق الـ SMC
        is_sweep = float(df['Low'].iloc[-1]) < ssl_level
        is_rejection = float(df['Close'].iloc[-1]) > ssl_level
        is_setup = bool(is_sweep and is_rejection)

        # عرض الواجهة
        st.markdown(f"""
            <div class="main-card">
                <span class="status-badge">🇬🇧 GBP / USD LIVE</span>
                <div class="price-text">{current_price:.5f}</div>
                <div style="margin: 15px 0;">
                    <span style="color: #8b949e;">RSI (14):</span> 
                    <span style="color: {'#ff4b4b' if rsi_val > 70 else '#00ff88'}; font-weight:bold;">{rsi_val}</span>
                </div>
                <hr style="border-color: #30363d;">
                <div style="display: flex; justify-content: space-around;">
                    <div>
                        <small style="color: #8b949e;">Liquidity (SSL)</small><br>
                        <b style="font-size: 1.2rem;">{ssl_level:.5f}</b>
                    </div>
                    <div>
                        <small style="color: #8b949e;">Market Structure</small><br>
                        <b style="color: {'#00ff88' if is_setup else '#8b949e'}; font-size: 1.2rem;">
                            {'🚨 ENTRY!' if is_setup else 'Scanning...'}
                        </b>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if is_setup:
            send_telegram(f"🚀 فرصة قنص على الباوند!\nالسعر: {current_price:.5f}\nالسبب: سحب سيولة (Liquidity Sweep)")
            st.balloons()

    else:
        st.warning("🔄 جاري انتظار جلب بيانات السوق...")

except Exception as e:
    st.error(f"⚠️ مشكلة فنية مؤقتة في البيانات.. جاري المحاولة مرة أخرى")

# تحديث الصفحة
time.sleep(15)
st.rerun()
