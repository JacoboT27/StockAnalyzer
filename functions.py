import yfinance as yf

def compute_rsi(series, period=21):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

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