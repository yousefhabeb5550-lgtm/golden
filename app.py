import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. إعدادات الهوية والتليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_gold_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🪙 **[قناص الذهب]**\n{message}", "parse_mode": "Markdown"})
    except Exception as e:
        st.error(f"خطأ في التليجرام: {e}")

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="Gold Sniper SMC", page_icon="🪙")

# --- 3. جلب البيانات (مع معالجة الأخطاء) ---
@st.cache_data(ttl=30)  # تحديث كل 30 ثانية
def fetch_data():
    try:
        # استخدام XAUUSD=X للسعر الفوري
        data = yf.download(tickers="XAUUSD=X", period="1d", interval="1m", progress=False)
        return data
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
        return pd.DataFrame()

df = fetch_data()

# --- 4. التحقق من وجود بيانات ---
if df.empty or len(df) < 5:
    st.warning("⚠️ جاري انتظار بيانات السوق... تأكد من اتصال الإنترنت.")
else:
    # الحصول على السعر الحالي
    price = round(float(df['Close'].iloc[-1]), 2)
    
    # --- 5. منطق SMC (بسيط وفعال) ---
    # سحب سيولة (النظر لآخر 15 دقيقة)
    recent_low = float(df['Low'].iloc[-15:-1].min())
    is_sweep = float(df['Low'].iloc[-1]) < recent_low and price > recent_low
    
    # فجوة سعرية (FVG)
    has_fvg = float(df['Low'].iloc[-1]) > float(df['High'].iloc[-3])

    # --- 6. الواجهة الرسومية ---
    st.title("🪙 رادار الذهب (SMC Edition)")
    
    col1, col2 = st.columns(2)
    col1.metric("سعر الذهب (المنصة)", f"${price}")
    col2.metric("حالة السيولة", "سحب سيولة ✅" if is_sweep else "انتظار...")

    if has_fvg:
        st.success("🔥 تم رصد فجوة سعرية (FVG) - الدخول قوي!")

    # --- 7. إرسال التنبيه ---
    if is_sweep and has_fvg:
        if 'last_alert_gold' not in st.session_state or st.session_state.last_alert_gold != price:
            msg = f"🚀 إشارة شراء مؤكدة!\n💰 السعر: {price}\n🛑 الستوب: {price - 0.50}\n🎯 الهدف: {price + 1.50}"
            send_gold_alert(msg)
            st.session_state.last_alert_gold = price

    # --- 8. زر الاختبار (في القائمة الجانبية) ---
    if st.sidebar.button("🚀 اختبار التليجرام"):
        send_gold_alert(f"فحص ناجح! السعر الحالي: {price}")
        st.sidebar.success("تم الإرسال!")
        
