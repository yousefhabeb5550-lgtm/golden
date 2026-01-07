import streamlit as st
import pandas as pd
import requests

# --- إعداداتك التي تعمل بنجاح ---
API_KEY = "451c070966a33f11467475f78230533a-0e99b0c2a507c336585189286f03d211"
ACCOUNT_ID = "101-004-30155050-001"
# نستخدم XAU_USD وهو المعيار العالمي للذهب الفوري
SYMBOL = "XAU_USD"

TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

st.set_page_config(page_title="Gold Sniper Final", page_icon="🪙")

def get_oanda_price():
    # هذا الرابط هو الأكثر استقراراً لجلب السعر اللحظي فقط
    url = f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}/pricing"
    params = {"instruments": SYMBOL}
    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            price_data = response.json()['prices'][0]
            # نأخذ متوسط سعر البيع والشراء ليتطابق مع شارت المنصة
            return (float(price_data['closeoutBid']) + float(price_data['closeoutAsk'])) / 2
    except:
        return None

price = get_oanda_price()

st.title("🪙 قناص الذهب (تزامن Oanda)")

if price:
    st.metric("سعر منصة Oanda المباشر", f"${price:,.2f}")
    st.write("✅ هذا السعر يتم جلبه الآن بنفس طريقة اليورو.")
    
    # زر الاختبار للتليجرام
    if st.sidebar.button("🚀 اختبار التطابق"):
        url_tg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        msg = f"🪙 سعر الذهب من Oanda الآن: {price:,.2f}\nهل يطابق منصتك؟"
        requests.post(url_tg, data={"chat_id": CHAT_ID, "text": msg})
        st.sidebar.success("تم إرسال السعر لهاتفك!")
else:
    st.error("⚠️ فشل في جلب السعر. تأكد أن حساب Oanda يدعم تداول الذهب (XAU/USD).")

st.info("💡 ملاحظة: إذا وجدت فرقاً بسيطاً (سنتات)، فهذا طبيعي بسبب سرعة التحديث.")
        
