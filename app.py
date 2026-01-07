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

st.set_page_config(page_title="Gold Price Sync", page_icon="🪙")

# --- التحكم في مطابقة السعر (Sidebar) ---
st.sidebar.header("⚖️ معايرة السعر")
offset = st.sidebar.number_input("مقدار الفرق عن منصتك (بالدولار):", value=0.0, step=0.1)
st.sidebar.info("مثال: إذا كان سعر الرادار 4474 ومنصتك 4464، ضع الرقم -10.0")

@st.cache_data(ttl=10)
def get_gold_raw():
    # نستخدم GC=F لأنه الأكثر استقراراً في البيانات التاريخية
    df = yf.download("GC=F", period="1d", interval="1m", progress=False)
    return df

df = get_gold_raw()

if not df.empty:
    # السعر الأصلي من المصدر
    raw_price = float(df['Close'].iloc[-1])
    # السعر المعدل ليطابق منصتك تماماً
    synced_price = round(raw_price + offset, 2)
    
    # حساب السيولة بناءً على السعر المعدل
    raw_low = float(df['Low'].iloc[-20:-1].min())
    synced_low = round(raw_low + offset, 2)
    
    is_sweep = float(df['Low'].iloc[-1] + offset) < synced_low and synced_price > synced_low

    st.title("🪙 رادار الذهب (نسخة التطابق التام)")
    
    col1, col2 = st.columns(2)
    col1.metric("السعر في الرادار", f"${raw_price:.2f}")
    col1.caption("سعر المصدر العالمي")
    
    col2.metric("السعر في منصتك", f"${synced_price:.2f}", delta=f"{offset}")
    col2.caption("السعر المعتمد للتداول")

    st.markdown("---")
    st.write(f"🔍 **سيولة منصتك (SSL):** {synced_low}")

    if is_sweep:
        st.success("🎯 سحب سيولة! السعر الآن في منصتك كسر القاع وعاد.")
        send_alert(f"دخول ذهب بسعر منصتك: {synced_price}\nالستوب: {synced_price - 0.50}")

else:
    st.error("جاري الاتصال بالمزود...")

if st.sidebar.button("🚀 اختبار التطابق"):
    send_alert(f"اختبار السعر: {synced_price}\nهل هذا الرقم مطابق لمنصتك الآن؟")
    
