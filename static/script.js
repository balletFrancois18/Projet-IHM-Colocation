

/* 
 global
 */


 // PLANNING

// Les événements sont chargés en temps réel depuis /api/planning-events

const jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];
const heures = [6, 12, 18, 0];
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
  document.getElementById('semaine-label-text').textContent =
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

  // Affiche les événements réels (tâches + réservations)
  const events = window.planningData || [];
  for (const ev of events) {
    if (window.filtreType && window.filtreType !== 'tous' && ev.type !== window.filtreType) continue;
    const evDate = new Date(ev.date + 'T00:00:00');
    const evDay  = evDate.getDay();
    const jourIdx = evDay === 0 ? 6 : evDay - 1;
    const debutSemaine = new Date(lundi);
    const finSemaine   = new Date(lundi);
    finSemaine.setDate(lundi.getDate() + 6);
    finSemaine.setHours(23, 59, 59);
    if (evDate < debutSemaine || evDate > finSemaine) continue;
    const h = ev.heure;
    let slot;
    if (h < 12)       slot = 6;
    else if (h < 18)  slot = 12;
    else if (h < 24)  slot = 18;
    else              slot = 0;
    const cell = document.getElementById(`cell-${jourIdx}-${slot}`);
    if (cell) {
      const couleur = ev.couleur || '#7bafd4';
      const url = ev.type === 'tache' ? '/taches' : '/reservations';
      const personne = ev.personne || '';
      let label, tooltip;
      const heure = ev.heure_str || (ev.heure !== undefined ? String(ev.heure).padStart(2,'0') + 'h' : '');
      const heureFin = ev.heure_fin_str || '';
      const plage = heureFin ? `${heure} – ${heureFin}` : heure;
      if (ev.type === 'tache') {
        label = `Tâche : ${ev.titre}`;
        tooltip = `Tâche à faire : ${ev.titre} — ${personne}${plage ? ' à ' + plage : ''}`;
      } else {
        label = `Résa. salle ${ev.titre}`;
        tooltip = `Réservation de la salle ${ev.titre} — ${personne}${plage ? ' ' + plage : ''}`;
      }
      const shortLabel = label.length > 18 ? label.substring(0, 17) + '…' : label;
      const heureTag = plage ? `<span style="float:right;font-size:0.75em;font-weight:700;opacity:0.95;margin-left:4px;">${plage}</span>` : '';
      cell.innerHTML += `<a href="${url}" class="resa" style="background:${couleur};border-left-color:rgba(0,0,0,0.25);" title="${tooltip}">${heureTag}${shortLabel}<br><span style="font-size:0.85em;opacity:0.9;">${personne}</span></a>`;
    }
  }
}

window.filtreType = 'tous';
function setFiltreType(type, btn) {
  window.filtreType = type;
  document.querySelectorAll('.filtre-planning').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  afficherSemaine();
}

function changerSemaine(delta) {
  offsetSemaine += delta;
  afficherSemaine();
}

function allerADate(dateStr) {
  if (!dateStr) return;
  const cible = new Date(dateStr + 'T00:00:00');
  const lundiAujourdhui = getLundiSemaine(0);
  const lundiCible = new Date(cible);
  const jourCible = cible.getDay();
  const diffLundi = jourCible === 0 ? -6 : 1 - jourCible;
  lundiCible.setDate(cible.getDate() + diffLundi);
  const diffMs = lundiCible - lundiAujourdhui;
  offsetSemaine = Math.round(diffMs / (7 * 24 * 3600 * 1000));
  afficherSemaine();
}

function chargerEtAfficher() {
  fetch('/api/planning-events')
    .then(r => r.json())
    .then(data => {
      window.planningData = data;
      afficherSemaine();
    });
}

// Chargement initial puis rafraîchissement toutes les 30 secondes
document.addEventListener('DOMContentLoaded', function() {
  chargerEtAfficher();
  setInterval(chargerEtAfficher, 30000);
});



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

