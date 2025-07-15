fetch('/api/stock/NVDA')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: 'Close Price',
                    data: data.close,
                    borderColor: 'blue',
                    fill: false
                }]
            }
        });
    });
