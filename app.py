from flask import Flask, render_template, jsonify, request
import yfinance as yf
import numpy as np
from functions import compute_rsi, getDividendInfo, getStockInfo, linearRegression, getVixData, getSMA, SMATrend, getPriceMXN

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<ticker>')
def stock_api(ticker):

    # --- Basic Info ---
    period = request.args.get('period', '1y')                                           # 1 year is default period
    stock, beta, hist = getStockInfo(ticker, period)                                    # Stock information
    dividendRate, ex_div_date, dividendTail, payoutratio = getDividendInfo(stock)       # Dividend information

    # --- Close Data (CHART 1) ---
    close = hist['Close'].ffill()                                                       # Close data

    # --- Ln Data (CHART 2) ---
    ln_close = np.log(close)                                                            # Ln of Close data
    x, m, b, regression, r2 = linearRegression(ln_close)                                # Linear regression (y = mx + b)

    # --- RSI Data (CHART 3) --- 
    rsi_hist = stock.history(period='4mo')                                              # RSI Data
    rsi_close = rsi_hist['Close'].ffill()                                               # RSI Close
    rsi = compute_rsi(rsi_close)                                                        # Compute RSI
    rsi = rsi.dropna()                                                                  # Drop NaN
    rsi = rsi.tail(30)                                                                  # Last 30 values of RSI
    rsi_dates = rsi.index.strftime('%m-%d').tolist()                                    # Index Dates

    # --- SMA Data (CHART 4) --- 
    sma200, close_sma = getSMA(stock,200)                                               # SMA200 Data
    sma200 = sma200.tail(90)                                                            # Limit to 90 values
    sma20, close_sma = getSMA(stock,20)                                                 # SMA20 Data
    aligned_dates = sma200.index                                                        # Aligned Dates Inedx
    sma20_aligned = sma20.loc[aligned_dates]                                            # Align SMA20 Dates
    close_sma_aligned = close_sma.loc[aligned_dates]                                    # Align Close Data
    price_trend = SMATrend(close, sma20_aligned, sma200)                                # Price Trend Based on SMA

    # --- VIX Data (CHART 5) ---    
    vix_close, vix_sma5, vix_dates, vix_state, vix_trend, recent_vix, vix_close_full = getVixData() # VIX Data

    # --- XLY/XLP Ratio (CHART 6) ---
    xlp = yf.Ticker('XLP')                                                              # XLP Ticker
    xlp_hist = xlp.history(period='100d')                                               # XLP History
    xlp_close = xlp_hist['Close'].ffill().dropna()                                      # XLP Close
    xly = yf.Ticker('XLY')                                                              # XLY Ticker
    xly_hist = xly.history(period='100d')                                               # XLY History
    xly_close = xly_hist['Close'].ffill().dropna()                                      # XLY Close
    common_index = xlp_close.index.intersection(xly_close.index)                        # Common Index
    xlp_close = xlp_close.loc[common_index]                                             # Align XLP
    xly_close = xly_close.loc[common_index]                                             # Align XLY
    ratio = (xly_close / xlp_close).dropna()                                            # Ratio
    sma10_ratio = ratio.rolling(window=10).mean().dropna()                              # Ratio SMA10 
    aligned_index = sma10_ratio.index                                                   # Aligned Index
    ratio = ratio.loc[aligned_index]                                                    # Aligned Ratio
    ratio_dates = aligned_index.strftime('%m-%d').tolist()                              # Aligned Dates
    
    # --- Data Section ---
    cagr = np.exp(m*252) - 1                                                            # CAGR
    mxn_price, stock_currency, price = getPriceMXN(stock)                               # Exchange and Price in MXN
    
    # Correlation
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

    #financials
    pe_ratio = stock.info.get('trailingPE', 'N/A')
    market_cap = stock.info.get('marketCap', 'N/A')
    eps = stock.income_stmt
    pb_ratio = stock.info.get('priceToBook', 'N/A')
    ebitda = stock.info.get('ebitda', 'N/A')
    ps_ratio = stock.info.get('priceToSalesTrailing12Months', 'N/A')

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

    #cash flow
    cashflow = stock.cashflow  # DataFrame of quarterly cash flows

    if 'Operating Cash Flow' in cashflow.index and 'Capital Expenditure' in cashflow.index:
        # Free cash flow = Operating Cash Flow - Capital Expenditures
        op_cf = cashflow.loc["Operating Cash Flow"]
        capex = cashflow.loc["Capital Expenditure"]
        fcf_series = op_cf + capex  # capex is negative
        fcf_tail = [{"date": d.strftime("%Y-%m-%d"), "amount": round(fcf_series[d], 2)}for d in fcf_series.dropna().index[-5:]]
    else:
        fcf_tail = ['No Free Cash Flow Data']

    #results
    current_ln_price = ln_close.iloc[-1]
    predicted_ln_price = m * x[-1] + b

    if current_ln_price > predicted_ln_price + 0.01:  # Allow a small margin for floating point precision
        trend_position = "Above"
    elif current_ln_price < predicted_ln_price - 0.01:
        trend_position = "Below"
    else:
        trend_position = "On"

    return jsonify({
        'beta': beta,
        'cagr': round(cagr * 100, 2),
        'correlation': correlation,
        'dates': hist.index.strftime('%Y-%m-%d').tolist(),
        'close': close.tolist(),
        'ln': ln_close.tolist(),
        'ln_regression': regression.tolist(),
        'ln_equation': f"y = {m:.4f}x + {b:.4f}",
        'slope': m,
        'r2': round(r2, 2),
        'rsi': rsi.tolist(),
        'dates_rsi': rsi_dates,
        'vix': vix_close.tolist(),
        'vix_sma5': vix_sma5.tolist(),
        'vix_state': vix_state,
        'vix_trend': vix_trend,
        'dates_vix': vix_dates,
        'sma200': sma200.tolist(),
        'dates_sma200': aligned_dates.strftime('%m-%d').tolist(),
        'sma20': sma20_aligned.tolist(),
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
        'dividendTail': ([{'date': k.strftime('%y-%m-%d'), 'amount': v}for k, v in dividendTail.items()] if not dividendTail.empty else None),
        'pe_ratio': pe_ratio,
        'market_cap': market_cap,
        'eps': eps,
        'pb_ratio': pb_ratio,
        'ebitda': ebitda,
        'ps_ratio': ps_ratio,
        'freeCashflowTail': fcf_tail,
        'ln_position': trend_position,
        'price_trend': price_trend,
    })

if __name__ == '__main__':
    app.run(debug=True)