



# fichier depense

function ouvrirModalModifier(id, titre, montant, payeur) {
  document.getElementById('modal-titre').textContent = 'Modifier une charge';
  document.getElementById('modal-form').action = '/depenses/modifier/' + id;
  document.getElementById('input-titre').value   = titre;
  document.getElementById('input-montant').value = montant;
  document.getElementById('input-payeur').value  = payeur;
  document.getElementById('modal').classList.add('active');
}

function ouvrirModal(type) {
  document.getElementById('modal-titre').textContent = 'Ajouter une charge';
  document.getElementById('modal-form').action = "{{ url_for('depenses.ajouter_depense') }}";
  document.getElementById('input-titre').value   = '';
  document.getElementById('input-montant').value = '';
  document.getElementById('input-payeur').value  = '';
  document.getElementById('modal').classList.add('active');
}
