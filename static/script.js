let chart1 = null;

function fetchAll() {
  const ticker = document.getElementById("ticker").value.toUpperCase();
  const period = document.getElementById("period").value || "1mo";

  fetch(`/api/stock/${ticker}?period=${period}`)
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById("chart1").getContext("2d");

      if (chart1) chart1.destroy(); // destroy old chart to avoid overlap

      chart1 = new Chart(ctx, {
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
    })
    .catch(err => {
      console.error("Fetch failed:", err);
      alert("Failed to fetch stock data. Check console.");
    });
}
