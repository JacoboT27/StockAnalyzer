from flask import Flask, render_template, jsonify, request
import yfinance as yf
import numpy as np
from functions import compute_rsi, getDividendInfo, getStockInfo, linearRegression, getVixData, getSMA, SMATrend, getPriceMXN, getCorrelationVIX, getEPS, getCashflow
from functions import getTrendPosition, getRatioTrend, getDividendTrend, getTrend, getUSDMXNdata, getMXNTrend
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
    sma50_ratio = ratio.rolling(window=50).mean().dropna()                              # Ratio SMA50 
    aligned_index = sma50_ratio.index                                                   # Aligned Index
    ratio = ratio.loc[aligned_index]                                                    # Aligned Ratio
    ratio_dates = aligned_index.strftime('%m-%d').tolist()                              # Aligned Dates

    # --- USD/MXN Data (CHART 7) ---
    USDMXN_close, dates_USDMXN, USMXN_UpBand, USMXN_LowBand,USMXN_sma50 = getUSDMXNdata()                     # Get USD/MXN data
    
    # --- Data Section ---
    cagr = np.exp(m*252) - 1                                                            # CAGR
    mxn_price, stock_currency, price = getPriceMXN(stock)                               # Exchange and Price in MXN 
    correlation = getCorrelationVIX(close_sma,vix_close_full)                           # Correlation with VIX
    pe_ratio = stock.info.get('trailingPE', 'N/A')                                      # P/E Ratio
    market_cap = stock.info.get('marketCap', 'N/A')                                     # Market Cap
    eps = getEPS(stock)                                                                 # EPS
    pb_ratio = stock.info.get('priceToBook', 'N/A')                                     # P/B Ratio
    ebitda = stock.info.get('ebitda', 'N/A')                                            # EBITDA
    ps_ratio = stock.info.get('priceToSalesTrailing12Months', 'N/A')                    # P/S Ratio
    fcf_tail = getCashflow(stock)                                                       # Free Cashflow   
    
    # --- Result Section ---
    trend_position = getTrendPosition(ln_close, m, x, b)                                # Trend Postion of Stock
    price_trend = SMATrend(close, sma20_aligned, sma200)                                # Price Trend Based on SMA
    ratio_trend = getRatioTrend(ratio,sma50_ratio)                                      # Trend of XLY/XLP Ratio
    dividend_trend = getDividendTrend(dividendTail)                                     # Dividend Trend
    eps_trend = getTrend(eps,"EPS")                                                     # EPS Trend
    fcf_trend = getTrend(fcf_tail,"FCF")                                                # FCF Trend
    mxn_trend = getMXNTrend (USDMXN_close, USMXN_UpBand, USMXN_LowBand)                 # USD/MXN Trend

    # --- Return JSON ---
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
        'dates_USDMXN': dates_USDMXN,
        'USDMXN_close': USDMXN_close.tolist(),
        'USMXN_UpBand': USMXN_UpBand.tolist(),
        'USMXN_LowBand': USMXN_LowBand.tolist(),
        'USMXN_sma50': USMXN_sma50.tolist(),
        'sma200': sma200.tolist(),
        'dates_sma200': aligned_dates.strftime('%m-%d').tolist(),
        'sma20': sma20_aligned.tolist(),
        'close_sma': close_sma_aligned.tolist(),
        'ratio': ratio.tolist(),
        'dates_ratio': ratio_dates,
        'ratio_sma50': sma50_ratio.tolist(),
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
        'ratio_trend': ratio_trend,
        'dividend_trend': dividend_trend,
        'eps_trend': eps_trend,
        'fcf_trend': fcf_trend,
        'mxn_trend': mxn_trend
    })

if __name__ == '__main__':
    app.run(debug=True)