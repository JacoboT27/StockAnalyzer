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
    }, 5000); // every 30 seconds
  }
}

function fetchAndUpdate(ticker, period) {
  fetch(`/api/stock/${ticker}?period=${period}`)
    .then(res => res.json())
    .then(data => {
      updateCharts(data, ticker);
      updateTable(data);
    })
    .catch(err => {
      console.error("Fetch failed:", err);
      alert("Failed to fetch stock data. Check console.");
    });
}

function updateTable(data) {
  document.getElementById("beta").innerText = data.beta;
  document.getElementById("cagr").innerText = data.cagr;
  document.getElementById("usdmxn").innerText = data.usd_mxn;
  document.getElementById("price").innerText = data.price;
  document.getElementById("vix").innerText = data.recent_vix;
  document.getElementById("correlation").innerText = data.correlation;
  document.getElementById("ln-equation-label").innerText = data.ln_equation;
  document.getElementById("r2").innerText = `R²: ${data.r2}`;
  document.getElementById("dividendRate").innerText = `Dividend Rate: ${data.dividendRate}` || "Stock does not pay dividends";
  document.getElementById("ex_div_date").innerText = data.ex_div_date ? `Ex-Dividend Date: ${data.ex_div_date}` : "No Ex-Dividend Date";
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