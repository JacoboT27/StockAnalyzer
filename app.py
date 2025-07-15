from flask import Flask, render_template, jsonify, request
import yfinance as yf
import numpy as np

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

    return jsonify({
        'dates': hist.index.strftime('%Y-%m-%d').tolist(),
        'close': close.tolist(),
        'ln': ln_close.tolist(),
        'ln_regression': regression.tolist(),
        'ln_equation': f"y = {m:.4f}x + {b:.4f}"
    })

if __name__ == '__main__':
    app.run(debug=True)