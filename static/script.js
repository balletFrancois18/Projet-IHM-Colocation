

/* 
 global
 */

/* 
 fichier depense

 */

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


/*calendrier*/
  const evenements = [
  { jour: 1, heure: 6,  titre: "Yoga" },
  { jour: 0, heure: 12, titre: "Repas" },
  { jour: 2, heure: 12, titre: "Repas" },
  { jour: 3, heure: 12, titre: "Repas" },
  { jour: 1, heure: 23, titre: "Soirée" },
  { jour: 4, heure: 23, titre: "Soirée" },
];

const jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];
const heures = [6, 12, 18, 23];
const mois = ["Jan","Fév","Mar","Avr","Mai","Juin","Juil","Aoû","Sep","Oct","Nov","Déc"];
let offsetSemaine = 0;

function getLundiSemaine(offset) {
  const today = new Date();
  const jourSemaine = today.getDay(); // 0=dim, 1=lun...
  const diffLundi = jourSemaine === 0 ? -6 : 1 - jourSemaine;
  const lundi = new Date(today);
  lundi.setDate(today.getDate() + diffLundi + offset * 7);
  lundi.setHours(0, 0, 0, 0);
  return lundi;
}

function afficherSemaine() {
  const lundi = getLundiSemaine(offsetSemaine);
  const vendredi = new Date(lundi);
  vendredi.setDate(lundi.getDate() + 4);

  // Label semaine
  document.getElementById('semaine-label').textContent =
    `${lundi.getDate()} ${mois[lundi.getMonth()]} — ${vendredi.getDate()} ${mois[vendredi.getMonth()]} ${vendredi.getFullYear()}`;

  // En-têtes avec vraies dates
  for (let i = 0; i < 7; i++) {
    const date = new Date(lundi);
    date.setDate(lundi.getDate() + i);
    const el = document.getElementById(`jour-${i}`);
    if (el) el.textContent = `${jours[i]} ${date.getDate()}`;
  }

  // Vide toutes les cellules
  for (let j = 0; j < 7; j++) {
    for (const h of heures) {
      const cell = document.getElementById(`cell-${j}-${h}`);
      if (cell) cell.innerHTML = '';
    }
  }

  // Affiche les événements sur la semaine courante uniquement
  if (offsetSemaine === 0) {
    for (const ev of evenements) {
      const cell = document.getElementById(`cell-${ev.jour}-${ev.heure}`);
      if (cell) {
        cell.innerHTML = `<div class="resa">${ev.titre}</div>`;
      }
    }
  }
}

function changerSemaine(delta) {
  offsetSemaine += delta;
  afficherSemaine();
}

// Attend que le DOM soit prêt
document.addEventListener('DOMContentLoaded', afficherSemaine);