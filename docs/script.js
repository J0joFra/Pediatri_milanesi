async function fetchData() {
    const response = await fetch('https://api.yourdomain.com/your-endpoint'); // Modifica questo URL con il tuo endpoint API
    const data = await response.json();
    return data;
}

function createChart(data) {
    const ctx = document.getElementById('myChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.Name_med), // Usa il nome del medico come etichetta
            datasets: [{
                label: 'Medici Attivi',
                data: data.map(item => item.Open), // Usa il valore di 'Open' come dati
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

fetchData().then(createChart).catch(error => console.error('Errore nel recupero dei dati:', error));
