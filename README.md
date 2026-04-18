# Stock Dashboard App

This is a simple stock dashboard web application built with **Flask (Python)** on the backend and **HTML/CSS/JavaScript** on the frontend. It allows users to enter a stock ticker (e.g., `AAPL`, `MSFT`, `NVDA`) and visualize recent relevant metrics in a desired time-frame, powered by real-time data from the [Yahoo Finance API](https://pypi.org/project/yfinance/).

---

## Features

- Input any stock ticker to fetch data
- Display historical closing prices
- Technical indicators (SMA, RSI, volume)
- Clean UI using custom CSS

---

## Tech Stack

- **Backend:** Python + Flask + yfinance
- **Frontend:** HTML, CSS, JavaScript (Chart.js)
- **API:** Yahoo Finance via `yfinance`

---

## Installation

On the command terminal run this command to clone the repository:

```bash
git clone https://github.com/JacoboT27/StockAnalyzer.git
```
Open the Stock Analyzer directory then run the following command to set up your virtual environment:

```bash
 pip install -r requirements. txt 
 ```

To start the application run on the terminal:
```python
python app.py
```

Then you should see a  `* Running on http://127.0.0.1:5000` message. `Ctrl + click` on the link to open the app.

On the app, fill the input fields with the stock ticker, and the time frame you want to analyze (e.g. NVDA, 2y).
