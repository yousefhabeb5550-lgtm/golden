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

st.set_page_config(page_title="Gold Precise Sync", page_icon="🪙")

# --- لوحة المعايرة الجانبية ---
st.sidebar.header("⚖️ موازنة السعر اللحظي")
# هنا تضع الفرق الذي تلاحظه (مثلاً لو الرادار 4473 ومنصتك 4464، الفرق هو -9)
manual_offset = st.sidebar.number_input("مقدار التعديل (دولار):", value=-9.15, step=0.01)
st.sidebar.info("قم بتغيير هذا الرقم حتى يتطابق السعر الكبير مع سعر منصتك.")

@st.cache_data(ttl=5) # تحديث كل 5 ثوانٍ
def get_gold_fast():
    try:
        # نستخدم الرمز الأساسي ونعالج الفرق يدوياً لضمان السرعة
        df = yf.download("GC=F", period="1d", interval="1m", progress=False)
        return df
    except: return pd.DataFrame()

df = get_gold_fast()

st.title("🪙 رادار الذهب (المعايرة اليدوية)")

if not df.empty:
    raw_price = float(df['Close'].iloc[-1])
    # السعر الذي سيظهر لك ويُرسل للتليجرام بعد المعايرة
    final_price = round(raw_price + manual_offset, 2)
    
    # عرض السعر المطابق
    st.metric("سعر منصتك الآن", f"${final_price}", delta=f"Offset: {manual_offset}")
    
    # حساب السيولة بناءً على السعر المعدل
    recent_low_raw = float(df['Low'].iloc[-20:-1].min())
    synced_low = round(recent_low_raw + manual_offset, 2)
    
    st.write(f"🔍 دعم السيولة في منصتك: {synced_low}")

    # منطق القنص (SMC)
    is_sweep = (df['Low'].iloc[-1] + manual_offset) < synced_low and final_price > synced_low

    if is_sweep:
        st.success("🎯 سحب سيولة! السعر كسر قاع منصتك وعاد.")
        send_alert(f"فرصة شراء!\nالسعر: {final_price}\nالستوب: {final_price - 0.50}")

else:
    st.error("جاري الاتصال... تأكد من تحديث الصفحة")

# زر الاختبار
if st.sidebar.button("🚀 اختبار التطابق"):
    send_alert(f"فحص السعر المعدل: {final_price}\nهل هذا مطابق تماماً لما تراه؟")
