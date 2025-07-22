from flask import Flask, render_template, jsonify, request
import yfinance as yf
import numpy as np
from sklearn.metrics import r2_score

def compute_rsi(series, period=21):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

    delta_days = (end_date - start_date).days
    years = delta_days / 365.25
    cagr = (end_price / start_price) ** (1 / years) - 1
    return cagr

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<ticker>')
def stock_api(ticker):
    period = request.args.get('period', '1mo')
    stock = yf.Ticker(ticker)
    beta = stock.info.get("beta", "N/A")
    hist = stock.history(period=period)
    dividendRate = stock.info.get('dividendRate', None)
    ex_div_date = stock.info.get('exDividendDate', None)
    dividendTail = stock.dividends.tail(5)
    payoutratio = stock.info.get("payoutRatio", None)

    close = hist['Close'].fillna(method='ffill')
    ln_close = np.log(close)

    # Linear regression (y = mx + b)
    x = np.arange(len(ln_close))
    m, b = np.polyfit(x, ln_close, 1)
    regression = m * x + b
    r2 = r2_score(ln_close, regression)

    #2mo for rsi
    rsi_hist = stock.history(period='4mo')
    rsi_close = rsi_hist['Close'].fillna(method='ffill')
    # Compute RSI
    rsi = compute_rsi(rsi_close)
    # Filter out NaN values for RSI
    rsi = rsi.dropna()
    # last 30 values of RSI
    rsi = rsi.tail(30)
    rsi_dates = rsi.index.strftime('%m-%d').tolist()

    #VIX 3months
    vix = yf.Ticker('^VIX')
    vix_hist = vix.history(period='5y')
    vix_close = vix_hist['Close'].fillna(method='ffill')
    vix_close_full = vix_close.dropna()
    vix_close = vix_close_full.tail(30)  # Last 30 days
    vix_dates = vix_close.index.strftime('%Y-%m-%d').tolist()
    #VIX sma5
    vix_sma5 = vix_close.rolling(window=5).mean()
    vix_sma5 = vix_sma5.dropna()
    vix_dates = vix_sma5.index.strftime('%m-%d').tolist()
    recent_vix = vix.info.get('regularMarketPrice', 0)

    #Stock sma200
    sma200_hist = stock.history(period='5y')
    sma200_close = sma200_hist['Close'].fillna(method='ffill')
    sma200 = sma200_close.rolling(window=200).mean().dropna().tail(90)  # Last 3 months
    #Stock sma10
    sma10 = sma200_close.rolling(window=10).mean().dropna()
    #Stock close
    close_sma = sma200_hist['Close'].fillna(method='ffill').dropna()
    # Align all series based on SMA200's index
    aligned_dates = sma200.index
    sma10_aligned = sma10.loc[aligned_dates]
    close_sma_aligned = close_sma.loc[aligned_dates]

    #calculate CAGR with slope of ln
    cagr = np.exp(m*252) - 1

    #XLP data
    xlp = yf.Ticker('XLP')
    xlp_hist = xlp.history(period='100d')
    xlp_close = xlp_hist['Close'].fillna(method='ffill').dropna()
    #XLY data
    xly = yf.Ticker('XLY')
    xly_hist = xly.history(period='100d')
    xly_close = xly_hist['Close'].fillna(method='ffill').dropna()
    # Align indices
    common_index = xlp_close.index.intersection(xly_close.index)
    xlp_close = xlp_close.loc[common_index]
    xly_close = xly_close.loc[common_index]
    ratio = xly_close / xlp_close
    ratio = ratio.dropna()
    # SMA10 of the ratio
    sma10_ratio = ratio.rolling(window=10).mean().dropna()
    # Align dates for plotting
    aligned_index = sma10_ratio.index  # to keep the same dates for both lines
    ratio = ratio.loc[aligned_index]   # align original ratio with sma10
    ratio_dates = aligned_index.strftime('%m-%d').tolist()

    # USD/MXN current price
    usd_mxn = yf.Ticker('USDMXN=X')
    mxn_price = usd_mxn.info.get('regularMarketPrice', 0)
    stock_currency = stock.info.get('currency', 'USD')

    # Current Price for Mexico
    if stock_currency == 'USD':
        price = stock.info.get('regularMarketPrice', 0) * mxn_price
    if stock_currency == 'MXN':
        price = stock.info.get('regularMarketPrice', 0)

    #correlation between stock and VIX last 200 days
    sma200_close.index = sma200_close.index.tz_localize(None)
    vix_close_full.index = vix_close_full.index.tz_localize(None)
    common_index = sma200_close.index.intersection(vix_close_full.index).dropna()
    vix_aligned = vix_close_full.loc[common_index]
    stock_aligned = sma200_close.loc[common_index]
    # Drop any remaining NaNs (just in case)
    vix_aligned = vix_aligned.dropna()
    stock_aligned = stock_aligned.dropna()
    # Ensure equal length after dropna
    min_len = min(len(vix_aligned), len(stock_aligned))
    vix_aligned = vix_aligned[-min_len:]
    stock_aligned = stock_aligned[-min_len:]
    # Final correlation
    correlation = round(vix_aligned.corr(stock_aligned),3)

    return jsonify({
        'beta': beta,
        'cagr': round(cagr * 100, 2),
        'correlation': correlation,
        'dates': hist.index.strftime('%Y-%m-%d').tolist(),
        'close': close.tolist(),
        'ln': ln_close.tolist(),
        'ln_regression': regression.tolist(),
        'ln_equation': f"y = {m:.4f}x + {b:.4f}",
        'r2': round(r2, 2),
        'rsi': rsi.tolist(),
        'dates_rsi': rsi_dates,
        'vix': vix_close.tolist(),
        'vix_sma5': vix_sma5.tolist(),
        'dates_vix': vix_dates,
        'sma200': sma200.tolist(),
        'dates_sma200': aligned_dates.strftime('%m-%d').tolist(),
        'sma10': sma10_aligned.tolist(),
        'close_sma': close_sma_aligned.tolist(),
        'ratio': ratio.tolist(),
        'dates_ratio': ratio_dates,
        'ratio_sma10': sma10_ratio.tolist(),
        'usd_mxn': round(mxn_price,2),
        'stock_currency': stock_currency,
        'price': round(price, 2),
        'recent_vix': recent_vix,
        'dividendRate': dividendRate,
        'payoutratio': payoutratio,
        'ex_div_date': (
            None if ex_div_date is None
            else (
                ex_div_date.strftime('%Y-%m-%d')
                if hasattr(ex_div_date, 'strftime')
                else (
                    np.datetime64(ex_div_date, 's').astype('M8[D]').astype(str)
                    if isinstance(ex_div_date, int)
                    else str(ex_div_date)
                )
            )
        ),
        'dividendTail': ([{'date': k.strftime('%y-%m-%d'), 'amount': v}for k, v in dividendTail.items()] if not dividendTail.empty else None)
    })

if __name__ == '__main__':
    app.run(debug=True)