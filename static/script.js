// Ouvrir modal ajouter
function ouvrirModalAjouter() {
  document.getElementById('modal-ajouter').classList.add('active');
}

// Ouvrir modal modifier avec données pré-remplies
function ouvrirModalModifier(id, titre, montant, payeur) {
  document.getElementById('modifier-titre').value   = titre;
  document.getElementById('modifier-montant').value = montant;
  document.getElementById('modifier-payeur').value  = payeur;
  document.getElementById('form-modifier').action   = '/depenses/modifier/' + id;
  document.getElementById('modal-modifier').classList.add('active');
}

// Fermer un modal
function fermerModal(id) {
  document.getElementById(id).classList.remove('active');
}

// Fermer en cliquant dehors
document.querySelectorAll('.modal-overlay').forEach(function(overlay) {
  overlay.addEventListener('click', function(e) {
    if (e.target === this) this.classList.remove('active');
  });
});

// Fermer avec Escape
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(function(m) {
      m.classList.remove('active');
    });
  }
});