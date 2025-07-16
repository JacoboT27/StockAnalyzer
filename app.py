from flask import Flask, render_template, jsonify, request
import yfinance as yf
import numpy as np

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<ticker>')
def stock_api(ticker):
    period = request.args.get('period', '1mo')
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    close = hist['Close'].fillna(method='ffill')
    ln_close = np.log(close)

    # Linear regression (y = mx + b)
    x = np.arange(len(ln_close))
    m, b = np.polyfit(x, ln_close, 1)
    regression = m * x + b

    #1year for rsi
    rsi_hist = stock.history(period='2mo')
    rsi_close = rsi_hist['Close'].fillna(method='ffill')
    # Compute RSI
    rsi = compute_rsi(rsi_close)
    # Filter out NaN values for RSI
    rsi = rsi.dropna()
    # last 30 values of RSI
    rsi = rsi.tail(30)
    rsi_dates = rsi.index.strftime('%Y-%m-%d').tolist()

    #VIX 6months
    vix = yf.Ticker('^VIX')
    vix_hist = vix.history(period='3mo')
    vix_close = vix_hist['Close'].fillna(method='ffill')
    vix_close = vix_close.dropna()
    vix_dates = vix_close.index.strftime('%Y-%m-%d').tolist()
    #VIX sma5
    vix_sma5 = vix_close.rolling(window=5).mean()
    vix_sma5 = vix_sma5.dropna()
    vix_dates = vix_sma5.index.strftime('%Y-%m-%d').tolist()

    #Stock sma200
    sma200_hist = stock.history(period='2y')
    sma200_close = sma200_hist['Close'].fillna(method='ffill')
    sma200 = sma200_close.rolling(window=200).mean().dropna()
    #Stock sma10
    sma10 = sma200_close.rolling(window=10).mean().dropna()
    #Stock close
    close_sma = sma200_hist['Close'].fillna(method='ffill').dropna()
    # Align all series based on SMA200's index
    aligned_dates = sma200.index
    sma10_aligned = sma10.loc[aligned_dates]
    close_sma_aligned = close_sma.loc[aligned_dates]

    #XLP data
    xlp = yf.Ticker('XLP')
    xlp_hist = xlp.history(period='20d')
    xlp_close = xlp_hist['Close'].fillna(method='ffill').dropna()
    #XLY data
    xly = yf.Ticker('XLY')
    xly_hist = xly.history(period='20d')
    xly_close = xly_hist['Close'].fillna(method='ffill').dropna()
    # Align indices
    common_index = xlp_close.index.intersection(xly_close.index)
    xlp_close = xlp_close.loc[common_index]
    xly_close = xly_close.loc[common_index]
    ratio = xlp_close / xly_close
    ratio = ratio.dropna()
    ratio_dates = ratio.index.strftime('%Y-%m-%d').tolist()

    return jsonify({
        'dates': hist.index.strftime('%Y-%m-%d').tolist(),
        'close': close.tolist(),
        'ln': ln_close.tolist(),
        'ln_regression': regression.tolist(),
        'ln_equation': f"y = {m:.4f}x + {b:.4f}",
        'rsi': rsi.tolist(),
        'dates_rsi': rsi_dates,
        'vix': vix_close.tolist(),
        'vix_sma5': vix_sma5.tolist(),
        'dates_vix': vix_dates,
        'sma200': sma200.tolist(),
        'dates_sma200': aligned_dates.strftime('%Y-%m-%d').tolist(),
        'sma10': sma10_aligned.tolist(),
        'close_sma': close_sma_aligned.tolist(),
        'ratio': ratio.tolist(),
        'dates_ratio': ratio_dates,
    })

if __name__ == '__main__':
    app.run(debug=True)