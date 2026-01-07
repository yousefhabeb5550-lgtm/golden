import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- إعدادات التليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🪙 **[قناص الذهب]**\n{message}", "parse_mode": "Markdown"})
    except: pass

st.set_page_config(page_title="Gold Sniper Stable", page_icon="🪙")

# --- جلب البيانات بطريقة مستقرة ---
@st.cache_data(ttl=20)
def get_gold_stable():
    try:
        # تجربة جلب السعر الفوري المباشر
        data = yf.download("GC=F", period="1d", interval="1m", progress=False)
        if data.empty:
            data = yf.download("XAUUSD=X", period="1d", interval="1m", progress=False)
        return data
    except:
        return pd.DataFrame()

df = get_gold_stable()

st.title("🪙 منصة قنص الذهب (النسخة المستقرة)")

if df.empty or len(df) < 5:
    st.error("❌ فشل الاتصال بمزود البيانات. يرجى الضغط على زر التحديث.")
    if st.button("🔄 تحديث البيانات الآن"):
        st.rerun()
else:
    # الحصول على آخر سعر وإزالة أي قيم فارغة
    last_row = df.iloc[-1]
    price = round(float(last_row['Close']), 2)
    
    # حساب السيولة (SMC Logic)
    recent_low = float(df['Low'].iloc[-20:-1].min())
    is_sweep = float(last_row['Low']) < recent_low and price > recent_low
    
    # واجهة العرض
    st.metric("سعر الذهب الحالي", f"${price}")
    
    st.write(f"🔍 أدنى سيولة قريبة (SSL): {recent_low}")
    
    if is_sweep:
        st.success("✅ رصد سحب سيولة! هذه فرصة دخول مؤسساتية.")
    else:
        st.info("🔎 السوق في حالة استقرار حالياً.. بانتظار سحب السيولة.")

# القائمة الجانبية للتأكد من العمل
if st.sidebar.button("🚀 اختبار تليجرام"):
    send_alert(f"منصة الذهب تعمل! السعر الحالي: {price}")
    st.sidebar.success("تم الإرسال!")
    
