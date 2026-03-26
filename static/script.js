

/* 
 global
 */


 // PLANNING

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



//tâches

function ouvrirModal() {
      const overlay = document.getElementById('modal-overlay');
      if (overlay) overlay.style.display = 'flex';
    }

    function fermerModal() {
      const overlay = document.getElementById('modal-overlay');
      if (overlay) overlay.style.display = 'none';
    }

    function fermerModalOverlay(e) {
      if (e.target === document.getElementById('modal-overlay')) fermerModal();
    }

    function filtrer(statut, btn) {
      document.querySelectorAll('.filtre-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('.tache-card').forEach(card => {
        card.style.display = (statut === 'tous' || card.dataset.statut === statut) ? 'flex' : 'none';
      });
    }

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') fermerModal();
    });

function ouvrirModalModifier(id, titre, assignee) {
    const modal = document.getElementById('modal-modifier-overlay');
    const form = document.getElementById('form-modifier-tache');
    
    // On donne l'ID à l'URL du formulaire pour Flask
    form.action = "/taches/" + id + "/modifier";
    
    // On remplit les champs de la pop-up avec les données actuelles
    document.getElementById('edit-titre').value = titre;
    document.getElementById('edit-assignee').value = assignee;
    
    // On affiche la pop-up en mode "flex" pour qu'elle soit centrée
    modal.style.display = 'flex';
}

function fermerModalModifier() {
    document.getElementById('modal-modifier-overlay').style.display = 'none';
}

// Ferme la pop-up si on clique à côté de la boîte blanche
function fermerModalModifierOverlay(e) {
    if (e.target.id === 'modal-modifier-overlay') {
        fermerModalModifier();
    }
}

