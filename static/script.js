let chart1 = null;
let chart4 = null;

function fetchAll() {
  const ticker = document.getElementById("ticker").value.toUpperCase();
  const period = document.getElementById("period").value || "1mo";

  fetch(`/api/stock/${ticker}?period=${period}`)
    .then(res => res.json())
    .then(data => {
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
            fill: false,
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
                fill: false,
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
                beginAtZero: true   // 👇 this handles your second request too
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
