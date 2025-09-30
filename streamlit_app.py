import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Page title
st.title("Stock Data Dashboard 📈")

# Sidebar inputs
st.sidebar.header("My project")
ticker_symbol = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, MSFT)", value="MSFT")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-31"))
ma_window = st.sidebar.slider("Moving Average Window", min_value=5, max_value=50, value=20)

# Fetching data
st.write(f"Fetching data for **{ticker_symbol}** from {start_date} to {end_date}...")
data = yf.download(ticker_symbol, start=start_date, end=end_date)

if data.empty:
    st.error("No data found. Please check the ticker symbol or date range.")
    st.stop()

data['MA'] = data['Close'].rolling(window=ma_window).mean()

# Initialize Tabs
tabs = st.tabs(["📋 Raw Data", "📈 Price Chart", "📊 Volume Chart", "📏 Moving Averages", "💰 Dividends & Splits","📈Technical Indicators" ])

# Tab 1: Raw Data
with tabs[0]:
    st.subheader(f"Raw Data for {ticker_symbol}")
    st.write(data.tail())
    st.download_button("Download Data as CSV", data.to_csv(), file_name=f"{ticker_symbol}_data.csv")

# Tab 2: Closing Price Chart
with tabs[1]:
    if "Close" in data:
        st.subheader("Closing Price Over Time")
        st.line_chart(data['Close'])
    else:
        st.warning("Closing price data is not available for this stock.")

# Tab 3: Volume Chart
with tabs[2]:
    if "Volume" in data:
        st.subheader("Volume Over Time")
        st.bar_chart(data['Volume'])
    else:
        st.warning("Volume data is not available for this stock.")
        
# Tab 4: Moving Averages
with tabs[3]:
    st.subheader(f"Closing Price with {ma_window}-Day Moving Average")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data.index, data['Close'], label="Closing Price", color='blue')
    ax.plot(data.index, data['MA'], label=f"{ma_window}-Day Moving Average", color='orange')
    ax.set_title(f"Closing Price with {ma_window}-Day Moving Average")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    st.pyplot(fig)

# Tab 5: Dividends & Splits
with tabs[4]:
    st.subheader("Dividends & Splits")
    ticker = yf.Ticker(ticker_symbol)
    dividends = ticker.dividends
    splits = ticker.splits

    st.write("**Dividends:**")
    st.write(dividends if not dividends.empty else "No dividends found during this period.")
    st.write("**Splits:**")
    st.write(splits if not splits.empty else "No splits found during this period.")
# Tab 6: Technical Indicators
with tabs[5]:
    st.subheader("Technical Indicators & Candlestick Chart")

    # Fetch historical data
    data = ticker.history(period="6mo")
    data.dropna(inplace=True)

    # Calculate RSI
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Calculate MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # Display RSI and MACD
    st.write("**RSI (14-day):**")
    st.line_chart(data[['RSI']])
    st.write("**MACD & Signal Line:**")
    st.line_chart(data[['MACD', 'Signal']])

    # Candlestick chart
    import mplfinance as mpf
    from io import BytesIO
    import base64

    st.write("**Candlestick Chart:**")
    mpf_plot = mpf.plot(data, type='candle', style='charles', volume=True, mav=(12, 26), returnfig=True)
    fig, _ = mpf_plot
    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.image(buf)
