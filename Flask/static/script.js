// Funzione per filtrare i medici in base alla specializzazione
function filterDoctors() {
    const specialization = document.getElementById('specialization').value;
    const rows = document.querySelectorAll('tbody tr');

    rows.forEach(row => {
        const specializationCell = row.cells[1]; // Cambia l'indice in base alla colonna giusta
        const matches = specialization ? specializationCell.textContent === specialization : true;
        row.style.display = matches ? '' : 'none';
    });
}
