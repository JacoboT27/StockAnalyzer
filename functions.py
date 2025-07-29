import yfinance as yf
import numpy as np
from sklearn.metrics import r2_score

def getDividendInfo(stock):
    dividendRate = stock.info.get('dividendRate', None)
    ex_div_date = stock.info.get('exDividendDate', None)
    dividendTail = stock.dividends.tail(5)
    payoutratio = stock.info.get("payoutRatio", None)
    return dividendRate, ex_div_date, dividendTail, payoutratio

def getStockInfo(ticker, period):
    stock = yf.Ticker(ticker)
    beta = stock.info.get("beta", "N/A")
    hist = stock.history(period=period)
    return stock, beta, hist

def linearRegression(ln_close):
    x = np.arange(len(ln_close))                                                       
    m, b = np.polyfit(x, ln_close, 1)
    regression = m * x + b
    r2 = r2_score(ln_close, regression)
    return x, m, b, regression, r2

def compute_rsi(series, period=21):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def getVixData():
    vix = yf.Ticker('^VIX')                                                             # VIX ticker
    vix_hist = vix.history(period='5y')                                                 # VIX history
    vix_close = vix_hist['Close'].ffill()                                               # VIX Close
    vix_close_full = vix_close.dropna()                                                 # Drop NaN
    vix_close = vix_close_full.tail(30)                                                 # Last 30 values of VIX
    vix_dates = vix_close.index.strftime('%Y-%m-%d').tolist()                           # Index Dates
    vix_sma5 = vix_close.rolling(window=5).mean()                                       # VIX SMA5 
    vix_sma5 = vix_sma5.dropna()                                                        # Drop NaN
    vix_dates = vix_sma5.index.strftime('%m-%d').tolist()                               # Index Dates
    recent_vix = vix.info.get('regularMarketPrice', 0)                                  # Latest VIX Value
    if (recent_vix < 15):
        vix_state = "Low VIX - Market Calm ✅"                                         # VIX State
    elif (recent_vix < 20):
        vix_state = "Moderate VIX - Market Stable ✅"
    elif (recent_vix < 30):
        vix_state = "High VIX - Market Volatile ⚠️"
    else:
        vix_state = "Extreme VIX - Market Panic ❌"
    if (recent_vix >= vix_sma5.iloc[-1]):
        vix_trend = 'VIX Rising - Go to Safe Sectors ⚠️'                               # VIX Trend
    else:
        vix_trend = 'VIX Falling - Risk On ✅'

    return vix_close, vix_sma5, vix_dates, vix_state, vix_trend, recent_vix, vix_close_full

def getSMA(stock,window):
    sma_hist = stock.history(period='5y')
    close_sma = sma_hist['Close'].ffill().dropna()
    sma = close_sma.rolling(window).mean().dropna()
    return sma, close_sma

def SMATrend(close, sma20_aligned, sma200):
    if (close.iloc[-1] > sma20_aligned.iloc[-1]) and (close.iloc[-1] > sma200.iloc[-1]):
        price_trend = " Strong Uptrend ✅"
    elif (close.iloc[-1] > sma20_aligned.iloc[-1]) and (sma20_aligned.iloc[-1] < sma200.iloc[-1]):
        price_trend = "Long-Term Downtrend ❌"
    elif (close.iloc[-1] < sma20_aligned.iloc[-1]) and (sma20_aligned.iloc[-1] > sma200.iloc[-1]):
        price_trend = "Good Entry Point ✅"
    elif (close.iloc[-1] < sma20_aligned.iloc[-1]) and (sma20_aligned.iloc[-1] < sma200.iloc[-1]):
        price_trend = "Strong Downtrend ❌"
    elif (sma20_aligned.iloc[-1] > sma200.iloc[-1]) and (close.iloc[-1] < sma20_aligned.iloc[-1]):
        price_trend = "Short-Term Downtrend ⚠️"
    elif (sma20_aligned.iloc[-1] < sma200.iloc[-1]) and (close.iloc[-1] > sma20_aligned.iloc[-1]):
        price_trend = "Short-Term Uptrend ⚠️"
    else:
        price_trend = "No Clear Trend ⚠️"
    return price_trend

def getPriceMXN(stock):
    usd_mxn = yf.Ticker('USDMXN=X')                                                     # Exchange Rate
    mxn_price = usd_mxn.info.get('regularMarketPrice', 0)                               # Current Price of USD
    stock_currency = stock.info.get('currency', 'USD')                                  # Currency of Stock
    if stock_currency == 'USD':
        price = stock.info.get('regularMarketPrice', 0) * mxn_price                     # Price in MXN
    if stock_currency == 'MXN':
        price = stock.info.get('regularMarketPrice', 0)
    return mxn_price, stock_currency, price