function ouvrirModalAjouter() {
    document.getElementById('modal-ajouter').classList.add('active');
}

function ouvrirModalModifier(id, titre, montant, payeur) {
    document.getElementById('modifier-titre').value   = titre;
    document.getElementById('modifier-montant').value = montant;
    document.getElementById('modifier-payeur').value  = payeur;
    document.getElementById('form-modifier').action   = '/depenses/modifier/' + id;
    document.getElementById('modal-modifier').classList.add('active');
}

function fermerModal(id) {
    document.getElementById(id).classList.remove('active');
}

document.querySelectorAll('.modal-overlay').forEach(function(overlay) {
    overlay.addEventListener('click', function(e) {
        if (e.target === this) this.classList.remove('active');
    });
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(function(m) {
            m.classList.remove('active');
        });
    }
});