from flask import Flask, render_template, jsonify, request
import yfinance as yf

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<ticker>')
def stock_api(ticker):
    period = request.args.get('period', '1mo')
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        data = {
            'dates': hist.index.strftime('%Y-%m-%d').tolist(),
            'close': hist['Close'].fillna(method='ffill').tolist()
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)