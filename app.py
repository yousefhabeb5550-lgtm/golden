import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# --- إعدادات الواجهة ---
st.set_page_config(layout="wide", page_title="SMC Live Monitor")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- شريط الإعدادات الجانبي ---
st.sidebar.title("🛠 التحكم بالتحليل")
pair = st.sidebar.selectbox("الزوج", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTC-USD"], index=0)
timeframe = st.sidebar.selectbox("الإطار الزمني", ["15m", "1h", "4h", "1d"], index=1)
sensitivity = st.sidebar.slider("حساسية اكتشاف المناطق", 1, 10, 5)

# --- جلب البيانات ---
@st.cache_data(ttl=60) # تحديث كل دقيقة
def load_data(symbol, interval):
    df = yf.download(symbol, period="5d", interval=interval)
    return df

data = load_data(pair, timeframe)

# --- خوارزمية SMC المصغرة ---
def apply_smc(df):
    # تحديد Order Blocks (تبسيط: آخر شمعة هابطة قبل صعود قوي، والعكس)
    df['OB_Buy'] = (df['Close'] > df['Open']) & (df['Close'].shift(1) < df['Open'].shift(1)) & (df['Volume'] > df['Volume'].rolling(5).mean())
    df['OB_Sell'] = (df['Close'] < df['Open']) & (df['Close'].shift(1) > df['Open'].shift(1)) & (df['Volume'] > df['Volume'].rolling(5).mean())
    return df

df = apply_smc(data)

# --- الرسم البياني التفاعلي ---
fig = go.Figure()

# 1. رسم الشموع اليابانية (ألوان كلاسيكية)
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    increasing_line_color='#26a69a', decreasing_line_color='#ef5350',
    name="السعر الحالي"
))

# 2. رسم مناطق الشراء (Demand/Order Blocks) باللون الأخضر الشفاف
buy_zones = df[df['OB_Buy']].tail(3) # آخر 3 مناطق شراء
for index, row in buy_zones.iterrows():
    fig.add_shape(type="rect", x0=index, x1=df.index[-1], y0=row['Low'], y1=row['High'],
                  fillcolor="rgba(38, 166, 154, 0.2)", line_width=0, name="منطقة شراء")

# 3. رسم مناطق البيع (Supply/Order Blocks) باللون الأحمر الشفاف
sell_zones = df[df['OB_Sell']].tail(3) # آخر 3 مناطق بيع
for index, row in sell_zones.iterrows():
    fig.add_shape(type="rect", x0=index, x1=df.index[-1], y0=row['Low'], y1=row['High'],
                  fillcolor="rgba(239, 83, 80, 0.2)", line_width=0, name="منطقة بيع")

fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False,
                  title=f"تحليل تدفق السيولة لـ {pair}", yaxis_title="السعر")

# --- العرض في التطبيق ---
col1, col2 = st.columns([3, 1])
with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💡 حالة السوق")
    last_price = df['Close'].iloc[-1]
    st.metric("السعر الحالي", f"{last_price:.5f}")
    
    if not buy_zones.empty and last_price <= buy_zones['High'].iloc[-1]:
        st.success("السعر حالياً في منطقة شراء (Demand)")
    elif not sell_zones.empty and last_price >= sell_zones['Low'].iloc[-1]:
        st.error("السعر حالياً في منطقة بيع (Supply)")
    else:
        st.info("السعر في منطقة تعادل (Wait for OB)")
