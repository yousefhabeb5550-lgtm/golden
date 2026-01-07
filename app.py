import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz
import requests

# --- إعدادات التليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_gold_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    except: pass

# --- إعدادات الذهب (إدارة المخاطر) ---
GOLD_SYMBOL = "GC=F" # عقود الذهب الآجلة (أكثر دقة لـ SMC)
SL_POINTS = 0.50     # 50 نقطة ذهب
TP_POINTS = 1.50     # 150 نقطة ذهب (1:3)

st.set_page_config(page_title="Gold Sniper V1", layout="wide")

# --- منطق الاستخراج الفني (SMC) ---
def get_gold_data():
    df = yf.Ticker(GOLD_SYMBOL).history(period="1d", interval="1m")
    return df

df = get_gold_data()

if not df.empty:
    price = round(df['Close'].iloc[-1], 2)
    # 1. تحديد السيولة (أعلى وأدنى نقطة في آخر 20 دقيقة)
    recent_high = df['High'].iloc[-20:-1].max()
    recent_low = df['Low'].iloc[-20:-1].min()
    
    # 2. فحص سحب السيولة (Sweep)
    is_liquidity_sweep_buy = df['Low'].iloc[-1] < recent_low and df['Close'].iloc[-1] > recent_low
    
    # 3. فحص الفجوة السعرية (FVG)
    # شمعة 1 (قبل السابقة) و شمعة 3 (الحالية)
    fvg_bullish = df['Low'].iloc[-1] > df['High'].iloc[-3]
    
    # 4. توقيت نيويورك (Silver Bullet)
    libya_tz = pytz.timezone('Africa/Tripoli')
    now_hour = datetime.now(libya_tz).hour
    is_silver_bullet_time = (15 <= now_hour <= 16) # من 3 لـ 4 عصراً

    # --- منطق اتخاذ القرار ---
    if is_liquidity_sweep_buy and fvg_bullish:
        entry = price
        sl = entry - SL_POINTS
        tp = entry + TP_POINTS
        
        status = "🔥 إشارة SILVER BULLET" if is_silver_bullet_time else "🪙 قنص ذهب عالي الجودة"
        
        msg = (f"{status}\n\n"
               f"📊 الأداة: GOLD (XAU/USD)\n"
               f"⚡️ النوع: BUY (SMC Logic)\n"
               f"🎯 الدخول: {entry}\n"
               f"🛑 الستوب: {sl}\n"
               f"✅ الهدف: {tp}\n\n"
               f"🛡️ التكتيك: سحب سيولة + فجوة سعرية (FVG)")
        
        # لمنع تكرار الإرسال في نفس الدقيقة
        if 'last_gold_time' not in st.session_state or st.session_state.last_gold_time != df.index[-1]:
            send_gold_alert(msg)
            st.session_state.last_gold_time = df.index[-1]

    # --- واجهة المنصة ---
    st.title("🪙 منصة قنص الذهب (SMC Edition)")
    c1, c2, c3 = st.columns(3)
    c1.metric("سعر أونصة الذهب", f"${price}")
    c2.metric("حالة السيولة", "سحب سيولة (Sweep) 🚨" if is_liquidity_sweep_buy else "مستقرة")
    c3.metric("توقيت نيويورك", "نشط ⚡️" if is_silver_bullet_time else "خامل")

    st.write(f"🔍 **أقرب سيولة شرائية (BSL):** {recent_high}")
    st.write(f"🔍 **أقرب سيولة بيعية (SSL):** {recent_low}")
    
    if fvg_bullish:
        st.success("✅ تم اكتشاف فجوة سعرية (FVG) - زخم مؤسساتي قوي!")
    
# --- إضافة زر الاختبار في القائمة الجانبية ---
st.sidebar.title("🛠️ إعدادات القناص")
if st.sidebar.button("🚀 اختبار اتصال التليجرام"):
    send_gold_alert("✅ فحص الاتصال ناجح! منصة الذهب متصلة وجاهزة للصيد.")
    st.sidebar.success("تم إرسال رسالة الاختبار بنجاح!")

st.sidebar.markdown("---")
st.sidebar.write("📌 **قاعدة الذهب:**")
st.sidebar.info("انتظر سحب السيولة (Sweep) ثم ظهور الفجوة (FVG) قبل الدخول.")
