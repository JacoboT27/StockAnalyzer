let chart1 = null, chart2 = null, chart3 = null, chart4 = null, chart5 = null, chart6 = null;
let lastTicker = "";
let lastPeriod = "";
let refreshIntervalStarted = false;

function fetchAll() {
  lastTicker = document.getElementById("ticker").value.toUpperCase();
  lastPeriod = document.getElementById("period").value || "1mo";

  fetchAndUpdate(lastTicker, lastPeriod);

  if (!refreshIntervalStarted) {
    refreshIntervalStarted = true;

    setInterval(() => {
        if (lastTicker && lastPeriod) {
        fetch(`/api/stock/${lastTicker}?period=${lastPeriod}`)
            .then(res => res.json())
            .then(data => {
            updateTable(data);
            });
        }
    }, 5000); // every 5 seconds
  }
}

function fetchAndUpdate(ticker, period) {
  fetch(`/api/stock/${ticker}?period=${period}`)
    .then(res => res.json())
    .then(data => {
      updateCharts(data, ticker);
      updateTable(data);
      updateDividends(data,ticker);
      updateFinancials(data);
    })
    .catch(err => {
      console.error("Fetch failed:", err);
      alert("Failed to fetch stock data. Check console.");
    });
}

function updateTable(data) {
  document.getElementById("beta").innerText = `Beta: ${data.beta}`;
  document.getElementById("cagr").innerText = `CAGR: ${data.cagr}`;
  document.getElementById("currency").innerText = `Currency: ${data.stock_currency}`;
  document.getElementById("usdmxn").innerText = `USD/MXN: ${data.usd_mxn}`;
  document.getElementById("price").innerText = `Price: ${data.price}`;
  document.getElementById("vix").innerText = `VIX: ${data.recent_vix}`;
  document.getElementById("correlation").innerText = `Correlation: ${data.correlation}`;
}

function updateFinancials(data) {
  document.getElementById("pe_ratio").innerText = data.pe_ratio !== 'N/A' ? `P/E Ratio: ${data.pe_ratio}` : "N/A";
  document.getElementById("market_cap").innerText = data.market_cap !== 'N/A' ? `Market Cap: $${(data.market_cap / 1e9).toFixed(2)}B` : "N/A";
  document.getElementById("eps").innerText = data.eps !== 'N/A' ? `EPS: $${data.eps}` : "N/A";
  document.getElementById("pb_ratio").innerText = data.pb_ratio !== 'N/A' ? `P/B Ratio: ${data.pb_ratio}` : "N/A";
  document.getElementById("ebitda").innerText = data.ebitda !== 'N/A' ? `EBITDA: $${(data.ebitda / 1e6).toFixed(2)}M` : "N/A";
  document.getElementById("ps_ratio").innerText = data.ps_ratio !== 'N/A' ? `P/S Ratio: ${data.ps_ratio}` : "N/A";
  const fcfList = document.getElementById("fcf-list");
  fcfList.innerHTML = "";
  data.freeCashflowTail.forEach(d => {
    const li = document.createElement("li");
    li.innerText = `${d.date}: $${d.amount.toLocaleString()}`;
    fcfList.appendChild(li);
  });
}

function updateDividends(data, ticker) {
  document.getElementById("dividendRate").innerText = data.dividendRate ? `Dividend Rate: ${data.dividendRate}` : `${ticker} does not pay dividends`;
  document.getElementById("ex_div_date").innerText = data.ex_div_date ? `Ex-Dividend Date: ${data.ex_div_date}` : "No Ex-Dividend Date";
  document.getElementById("payoutratio").innerText = data.payoutratio ? `Payout Ratio: ${parseFloat(data.payoutratio).toFixed(2)}` : "No Payout Ratio";
  const tailElement = document.getElementById("dividend-tail");
  tailElement.innerHTML = "";

  if (data.dividendTail && data.dividendTail.length > 0) {
    data.dividendTail.forEach(d => {
      const li = document.createElement("li");
      li.textContent = `${d.date}: $${parseFloat(d.amount).toFixed(2)}`;
      tailElement.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.textContent = "No recent dividends";
    tailElement.appendChild(li);
  }
}

function updateCharts(data, ticker) {
  // chart1 - close price
  const ctx1 = document.getElementById("chart1").getContext("2d");
  if (chart1) chart1.destroy();
  chart1 = new Chart(ctx1, {
    type: "line",
    data: {
      labels: data.dates,
      datasets: [{
        label: `${ticker} Close Price`,
        data: data.close,
        borderColor: "blue",
        backgroundColor: "rgba(0, 0, 255, 0.1)",
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 0
      }]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      scales:{x:{ticks:{color: "white"}}, y:{ticks:{color: "white"}}},
      plugins: {legend: {display: true, labels: {color: "white", font: { size: 18}}}, title: { display: false}}
    }
  });

  // chart2 - RSI
  const ctx2 = document.getElementById("chart2").getContext("2d");
  if (chart2) chart2.destroy();
  const oversoldLine = new Array(data.dates_rsi.length).fill(30);
  const overboughtLine = new Array(data.dates_rsi.length).fill(70);
  chart2 = new Chart(ctx2, {
    type: "line",
    data: {
      labels: data.dates_rsi,
      datasets: [
        { label: "RSI (21)", data: data.rsi, borderColor: "purple", fill: false, pointRadius: 0 },
        { label: "Oversold (30)", data: oversoldLine, borderColor: "red", borderDash: [5, 5], fill: false, pointRadius: 0 },
        { label: "Overbought (70)", data: overboughtLine, borderColor: "orange", borderDash: [5, 5], fill: false, pointRadius: 0 }
      ]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      scales:{x:{ticks:{color: "white"}}, y:{min: 0, max: 100, ticks:{color: "white", stepSize: 20}}},
      plugins: {legend: {display: true, labels: {color: "white", font: {size: 18}}}, title: {display: false}},
    }
  });

  // chart3 - SMA
  const ctx3 = document.getElementById("chart3").getContext("2d");
  if (chart3) chart3.destroy();
  chart3 = new Chart(ctx3, {
    type: "line",
    data: {
      labels: data.dates_sma200,
      datasets: [
        { label: "sma200", data: data.sma200, borderColor: "green", borderDash: [5, 5], fill: false, pointRadius: 0 },
        { label: "sma10", data: data.sma10, borderColor: "orange", borderDash: [5, 5], fill: false, pointRadius: 0 },
        { label: "close", data: data.close_sma, borderColor: "blue", fill: false, pointRadius: 0 }
      ]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      scales:{x:{ticks:{color: "white", autoSkip: true, maxTicksLimit: 15}}, y:{ticks:{color: "white", stepSize: 20}}},
      plugins: {legend: {display: true, labels: {color: "white", font: {size: 18}}}, title: {display: false}},
    }
  });

  // chart4 - ln price + regression
  document.getElementById("ln-equation-label").innerText = data.ln_equation;
  document.getElementById("r2").innerText = `R²: ${data.r2}`;
  const ctx4 = document.getElementById("chart4").getContext("2d");
  if (chart4) chart4.destroy();
  chart4 = new Chart(ctx4, {
    type: "line",
    data: {
      labels: data.dates,
      datasets: [
        { label: `${ticker} ln Price`, data: data.ln, borderColor: "green", backgroundColor: "rgba(0,255,0,0.1)", fill: true, pointRadius: 0 },
        { label: "Linear Regression", data: data.ln_regression, borderColor: "black", borderDash: [5, 5], fill: false, pointRadius: 0 }
      ]
    },
    options: {
     maintainAspectRatio: false,
      responsive: true,
      scales:{x:{ticks:{color: "white"}}, y:{ticks:{color: "white", stepSize: 0.1}}},
      plugins: {legend: {display: true, labels: {color: "white", font: {size: 18}}}, title: {display: false}},
    }
  });

  // chart5 - VIX + SMA5 + thresholds
  const ctx5 = document.getElementById("chart5").getContext("2d");
  if (chart5) chart5.destroy();
  const neutral = new Array(data.dates_vix.length).fill(15);
  const volatile = new Array(data.dates_vix.length).fill(20);
  const panic = new Array(data.dates_vix.length).fill(25);
  chart5 = new Chart(ctx5, {
    type: "line",
    data: {
      labels: data.dates_vix,
      datasets: [
        { label: "VIX", data: data.vix, borderColor: "orange", backgroundColor: "rgba(234, 109, 14, 0.1)", fill: true, pointRadius: 0 },
        { label: "VIX 5-day MA", data: data.vix_sma5, borderColor: "red", fill: false, pointRadius: 0 },
        { label: "Neutral (15)", data: neutral, borderColor: "green", borderDash: [5, 5], fill: false, pointRadius: 0 },
        { label: "Volatile (20)", data: volatile, borderColor: "blue", borderDash: [5, 5], fill: false, pointRadius: 0 },
        { label: "Panic (25)", data: panic, borderColor: "purple", borderDash: [5, 5], fill: false, pointRadius: 0 }
      ]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      scales:{x:{ticks:{color: "white"}}, y:{ticks:{color: "white", stepSize: 5}}},
      plugins: {legend: {display: true, labels: {color: "white", font: {size: 18}}}, title: {display: false}},
    }
  });

  // chart6 - XLY/XLP ratio
  const ctx6 = document.getElementById("chart6").getContext("2d");
  if (chart6) chart6.destroy();
  chart6 = new Chart(ctx6, {
    type: "line",
    data: {
      labels: data.dates_ratio,
      datasets: [
        { label: "ratio", data: data.ratio, borderColor: "red", backgroundColor: "rgba(255, 0, 0, 0.1)", fill: true, pointRadius: 0 },
        { label: "sma10", data: data.ratio_sma10, borderColor: "purple", borderDash: [5, 5], fill: false, pointRadius: 0 }
      ]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      scales:{x:{ticks:{color: "white", autoSkip: true}}, y:{ticks:{color: "white", stepSize: 0.05}}},
      plugins: {legend: {display: true, labels: {color: "white", font: {size: 18}}}, title: {display: false}},
    }
  });
}