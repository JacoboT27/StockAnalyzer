from flask import Flask, render_template, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stock/<ticker>")
def stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    data = {
        "dates": hist.index.strftime('%Y-%m-%d').tolist(),
        "close": hist["Close"].tolist()
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
