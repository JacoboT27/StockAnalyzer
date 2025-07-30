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

def getCorrelationVIX(close_sma, vix_close_full):
    close_sma.index = close_sma.index.tz_localize(None)
    vix_close_full.index = vix_close_full.index.tz_localize(None)
    common_index = close_sma.index.intersection(vix_close_full.index).dropna()
    vix_aligned = vix_close_full.loc[common_index]
    stock_aligned = close_sma.loc[common_index]
    # Drop any remaining NaNs (just in case)
    vix_aligned = vix_aligned.dropna()
    stock_aligned = stock_aligned.dropna()
    # Ensure equal length after dropna
    min_len = min(len(vix_aligned), len(stock_aligned))
    vix_aligned = vix_aligned[-min_len:]
    stock_aligned = stock_aligned[-min_len:]
    # Final correlation
    correlation = round(vix_aligned.corr(stock_aligned),3)
    return correlation

def getEPS(stock):
    eps = stock.income_stmt                                                             # EPS
    #check if eps has 'Diluted EPS' else return 'N/A'
    if 'Diluted EPS' in eps.index:
        eps_series = eps.loc["Diluted EPS"].dropna()

        # Columns are usually datetime or string, so parse if needed
        eps = []
        for d in eps_series.index[-5:]:
            # Try to parse date string to YYYY-MM-DD
            date_str = str(d)
            if "-" in date_str:
                date_fmt = date_str[:10]
            else:
                date_fmt = date_str
            amount = round(eps_series[d], 2)
            eps.append({"date": date_fmt, "amount": amount})
    # If no 'Diluted EPS', return empty list
    else:
        eps = ['No EPS Data']
    return eps

def getCashflow(stock):
    cashflow = stock.cashflow  # DataFrame of quarterly cash flows

    if 'Operating Cash Flow' in cashflow.index and 'Capital Expenditure' in cashflow.index:
        # Free cash flow = Operating Cash Flow - Capital Expenditures
        op_cf = cashflow.loc["Operating Cash Flow"]
        capex = cashflow.loc["Capital Expenditure"]
        fcf_series = op_cf + capex  # capex is negative
        fcf_tail = [{"date": d.strftime("%Y-%m-%d"), "amount": round(fcf_series[d], 2)}for d in fcf_series.dropna().index[-5:]]
    else:
        fcf_tail = ['No Free Cash Flow Data']
    return fcf_tail

def getTrendPosition(ln_close,m,x,b):
    current_ln_price = ln_close.iloc[-1]                                                # Current Ln Price
    predicted_ln_price = m * x[-1] + b                                                  # Current Predicted Price
    if current_ln_price > predicted_ln_price + 0.01: 
        trend_position = "Above"
    elif current_ln_price < predicted_ln_price - 0.01:
        trend_position = "Below"
    else:
        trend_position = "On"
    return trend_position

def getRatioTrend(ratio, sma50_ratio):
    if ratio.iloc[-1] < sma50_ratio.iloc[-1]:
        ratio_trend = 'Risk OFF Defensive Market ⚠️'
    else:
        ratio_trend = 'Risk ON Growth Market ✅'
    return ratio_trend