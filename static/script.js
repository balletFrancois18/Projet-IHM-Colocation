// Met à jour le montant d'une personne dans une catégorie
function majMontant(input) {
    const membre   = input.dataset.membre;
    const cat      = input.dataset.cat;
    const montant  = parseFloat(input.value) || 0;

    fetch('/depenses/maj', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
            payeur:    membre,
            categorie: cat,
            montant:   montant
        })
    })
    .then(r => r.json())
    .then(() => {
        // Recharge la page pour mettre à jour les barres
        location.reload();
    });
}

function ouvrirModalTotal() {
    const total = document.getElementById('affichage-total').textContent;
    document.getElementById('total-actuel').textContent = total;
    document.getElementById('modal-total').classList.add('active');
}

function fermerModal(id) {
    document.getElementById(id).classList.remove('active');
}

document.querySelectorAll('.modal-overlay').forEach(function(o) {
    o.addEventListener('click', function(e) {
        if (e.target === this) this.classList.remove('active');
    });
});