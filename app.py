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
manual_offset = st.sidebar.number_input("مقدار التعديل (دولار):", value=-9.15, step=0.01)

@st.cache_data(ttl=5)
def get_gold_fast():
    try:
        # جلب البيانات الخام
        df = yf.download("GC=F", period="1d", interval="1m", progress=False)
        return df
    except: return pd.DataFrame()

df = get_gold_fast()

st.title("🪙 رادار الذهب (المعايرة اليدوية)")

if not df.empty and len(df) > 20:
    # استخدام .item() لمنع خطأ ValueError الظاهر في صورتك
    raw_price = float(df['Close'].iloc[-1].item())
    final_price = round(raw_price + manual_offset, 2)
    
    # حساب السيولة
    raw_low_series = df['Low'].iloc[-20:-1]
    recent_low_raw = float(raw_low_series.min().item())
    synced_low = round(recent_low_raw + manual_offset, 2)
    
    # عرض السعر الكبير
    st.metric("سعر منصتك الآن", f"${final_price}")
    st.write(f"🔍 دعم السيولة في منصتك: {synced_low}")

    # إصلاح منطق القنص (تحويل كل شيء لـ float صريح)
    current_low_val = float(df['Low'].iloc[-1].item()) + manual_offset
    is_sweep = current_low_val < synced_low and final_price > synced_low

    if is_sweep:
        st.success("🎯 سحب سيولة (Sweep) مكتشف الآن!")
        send_alert(f"فرصة شراء!\nالسعر: {final_price}\nالهدف: {final_price + 1.50}")
else:
    st.warning("⚠️ بانتظار اكتمال بيانات السوق... يرجى التحديث بعد ثوانٍ.")

# زر الاختبار
if st.sidebar.button("🚀 اختبار التطابق"):
    send_alert(f"فحص السعر المعدل: {final_price}\nهل هذا مطابق تماماً لمنصتك؟")
    
