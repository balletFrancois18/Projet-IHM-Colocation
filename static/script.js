

/* 
 global
 */

/* 
 fichier depense

 */

function ouvrirModal() {
  document.getElementById('modal-titre').textContent = 'Ajouter une dépense';
  document.getElementById('modal-form').action = "{{ url_for('depenses.ajouter_depense') }}";
  document.getElementById('input-titre').value   = '';
  document.getElementById('input-montant').value = '';
  document.getElementById('input-payeur').value  = '';
  document.getElementById('modal').classList.add('active');
}

function ouvrirModalModifier(id, titre, montant, payeur) {
  document.getElementById('modal-titre').textContent = 'Modifier une dépense';
  document.getElementById('modal-form').action = '/depenses/modifier/' + id;
  document.getElementById('input-titre').value   = titre;
  document.getElementById('input-montant').value = montant;
  document.getElementById('input-payeur').value  = payeur;
  document.getElementById('modal').classList.add('active');
}

function fermerModal() {
  document.getElementById('modal').classList.remove('active');
}

document.getElementById('modal').addEventListener('click', function(e) {
  if (e.target === this) fermerModal();
});