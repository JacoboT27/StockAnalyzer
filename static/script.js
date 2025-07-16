let chart1 = null;
let chart2 = null;
let chart3 = null;
let chart4 = null;
let chart5 = null;
let chart6 = null;

function fetchAll() {
  const ticker = document.getElementById("ticker").value.toUpperCase();
  const period = document.getElementById("period").value || "1mo";

  fetch(`/api/stock/${ticker}?period=${period}`)
    .then(res => res.json())
    .then(data => {
      document.getElementById("beta").innerText = data.beta;
      const ctx1 = document.getElementById("chart1").getContext("2d");

      if (chart1) chart1.destroy(); // destroy old chart to avoid overlap

      chart1 = new Chart(ctx1, {
        type: "line",
        data: {
          labels: data.dates,
          datasets: [{
            label: `${ticker} Close Price`,
            data: data.close,
            borderColor: "blue",
            backgroundColor: "rgba(0, 0, 255, 0.1)", // light blue fill
            fill: true,
            pointRadius: 0,        // <-- hide points
            pointHoverRadius: 0    // <-- hide on hover too
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true
            },
            title: {
              display: false
            }
          }
        }
      });

      document.getElementById("ln-equation-label").innerText = data.ln_equation;
      const ctx4 = document.getElementById("chart4").getContext("2d");

      if (chart4) chart4.destroy(); // destroy old chart to avoid overlap

      chart4 = new Chart(ctx4, {
        type: "line",
        data: {
            labels: data.dates,
            datasets: [
            {
                label: `${ticker} ln Price`,
                data: data.ln,
                borderColor: "green",
                backgroundColor: "rgba(0, 255, 0, 0.1)", // light green fill
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 0
            },
            {
                label: "Linear Regression",
                data: data.ln_regression,
                borderColor: "black",
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            }
            ]
        },
        options: {
            responsive: true,
            plugins: {
            legend: { display: true },
            title: { display: false }
            },
            scales: {
            y: {
                ticks:{
                    stepSize: 0.1
                }
            }
            }
        }
        });

        const ctx2 = document.getElementById("chart2").getContext("2d");
        if (chart2) chart2.destroy();

        const rsiLabels = data.dates_rsi;
        const oversoldLine = new Array(rsiLabels.length).fill(30);
        const overboughtLine = new Array(rsiLabels.length).fill(70);

        chart2 = new Chart(ctx2, {
        type: "line",
        data: {
            labels: rsiLabels,
            datasets: [
            {
                label: "RSI (14)",
                data: data.rsi,
                borderColor: "purple",
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            },
            {
                label: "Oversold (30)",
                data: oversoldLine,
                borderColor: "red",
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            },
            {
                label: "Overbought (70)",
                data: overboughtLine,
                borderColor: "orange",
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
            legend: { display: true },
            title: { display: false }
            },
            scales: {
            y: {
                min: 0,
                max: 100,
                ticks: {
                stepSize: 20
                }
            }
            }
        }
        });

        const ctx5 = document.getElementById("chart5").getContext("2d");
        if (chart5) chart5.destroy();

        chart5 = new Chart(ctx5, {
        type: "line",
        data: {
            labels: data.dates_vix,
            datasets: [
            {
                label: "VIX",
                data: data.vix,
                borderColor: "blue",
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            },
            {
                label: "VIX 5-day MA",
                data: data.vix_sma5,
                borderColor: "red",
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
            legend: { display: true },
            title: { display: false }
            },
            scales: {
            y: {
                min: 0,
                ticks: {
                stepSize: 10
                }
            }
            }
        }
        });

        const ctx3 = document.getElementById("chart3").getContext("2d");
        if (chart3) chart3.destroy();

        chart3 = new Chart(ctx3, {
        type: "line",
        data: {
            labels: data.dates_sma200,
            datasets: [
            {
                label: "sma200",
                data: data.sma200,
                borderColor: "green",
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            },
            {
                label: "sma10",
                data: data.sma10,
                borderColor: "orange",
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            },
            {
                label: "close",
                data: data.close_sma,
                borderColor: "blue",
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
            legend: { display: true },
            title: { display: false }
            },
            scales: {
            x: {
                ticks: {
                autoSkip: true,
                maxTicksLimit: 20
                }
            },
            y: {
                ticks: {
                stepSize: 20
                }
            }
            }
        }
        });

        const ctx6 = document.getElementById("chart6").getContext("2d");
        if (chart6) chart6.destroy();

        chart6 = new Chart(ctx6, {
        type: "line",
        data: {
            labels: data.dates_ratio,
            datasets: [
            {
                label: "ratio",
                data: data.ratio,
                borderColor: "red",
                backgroundColor: "rgba(255, 0, 0, 0.1)", // light red fill
                fill: true,
                pointRadius: 0,
                pointHoverRadius: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
            legend: { display: true },
            title: { display: false }
            },
            scales: {
            x: {
                ticks: {
                autoSkip: true,
                //maxTicksLimit: 20
                }
            },
            y: {
                ticks: {
                stepSize: 0.1
                }
            }
            }
        }
        });


    })
    .catch(err => {
      console.error("Fetch failed:", err);
      alert("Failed to fetch stock data. Check console.");
    });
}
