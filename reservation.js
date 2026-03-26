/* ─── DONNÉES ───────────────────────────────────────────────
   Liste des espaces disponibles dans l'appartement.
   On s'en sert pour générer les cartes de la sidebar
   et pour associer un emoji à chaque salle.
   ─────────────────────────────────────────────────────────── */
const ROOMS = [
  { name: 'Salle de bain', emoji: '🚿' },
  { name: 'Salon',         emoji: '🛋️' },
  { name: 'Cuisine',       emoji: '🍳' },
  { name: 'Global',        emoji: '🏠' },
];

/* Tableau principal des réservations.
   Chaque objet = une ligne dans le tableau HTML.
   En production, ces données viendraient d'une base de données. */
let reservations = [
  { id: 1, date: '2026-03-20', profil: 'OL', salle: 'Salle de bain', statut: 'Disponible', debut: '10:00', fin: '11:00' },
  { id: 2, date: '2026-03-20', profil: 'OB', salle: 'Salon',         statut: 'Occupé',     debut: '12:00', fin: '13:30' },
  { id: 3, date: '2026-03-21', profil: 'OE', salle: 'Cuisine',       statut: 'Réservé',    debut: '08:00', fin: '09:00' },
];

/* Compteur auto-incrémenté pour générer des IDs uniques */
let nextId = 4;

/* Stocke l'ID de la réservation en cours de modification
   (null = on est en mode "ajout") */
let editingId = null;


/* ─── POINT D'ENTRÉE ────────────────────────────────────────
   render() est appelé au chargement et à chaque modification
   des données. Il redessine le tableau et la sidebar.
   ─────────────────────────────────────────────────────────── */
function render() {
  renderTable();
  renderRooms();
}


/* ─── RENDU DU TABLEAU ──────────────────────────────────────
   On vide le <tbody>, on trie les réservations par date puis
   par heure, puis on recrée une <tr> pour chacune.
   ─────────────────────────────────────────────────────────── */
function renderTable() {
  const tbody   = document.getElementById('tableBody');
  const empty   = document.getElementById('emptyState');

  tbody.innerHTML = '';

  /* Tri : d'abord par date, ensuite par heure de début */
  const sorted = [...reservations].sort((a, b) =>
    a.date.localeCompare(b.date) || a.debut.localeCompare(b.debut)
  );

  if (sorted.length === 0) {
    empty.style.display = 'block';
    return;
  }

  empty.style.display = 'none';

  sorted.forEach((r, index) => {
    const tr = document.createElement('tr');

    /* Décalage d'animation pour que les lignes apparaissent
       les unes après les autres */
    tr.style.animationDelay = `${index * 0.04}s`;

    /* innerHTML : on construit le HTML de la ligne via un
       template literal (les backticks ``).
       Les ${} permettent d'insérer des variables JS. */
    tr.innerHTML = `
      <td>${formatDate(r.date)}</td>
      <td><strong>${r.profil}</strong></td>
      <td>
        <span class="room-icon">
          <span>${roomEmoji(r.salle)}</span>
          ${r.salle}
        </span>
      </td>
      <td>
        <span class="badge badge-${statusClass(r.statut)}">
          ● ${r.statut}
        </span>
      </td>
      <td>${r.debut}</td>
      <td>${r.fin}</td>
      <td>
        <div class="actions">
          <button class="btn btn-ghost"         onclick="openEditModal(${r.id})" title="Modifier">✏️</button>
          <button class="btn btn-danger-ghost"  onclick="deleteReservation(${r.id})" title="Supprimer">🗑</button>
        </div>
      </td>
    `;

    tbody.appendChild(tr);
  });
}


/* ─── RENDU DES CARTES DE SALLES ────────────────────────────
   Pour chaque salle, on vérifie si une réservation est
   en cours à cet instant (aujourd'hui + maintenant).
   ─────────────────────────────────────────────────────────── */
function renderRooms() {
  const grid = document.getElementById('roomsGrid');
  grid.innerHTML = '';

  const today = new Date().toISOString().split('T')[0];         /* ex: "2026-03-19" */
  const now   = new Date().toTimeString().slice(0, 5);          /* ex: "14:35"       */

  ROOMS.forEach(room => {

    /* Y a-t-il une réservation ACTIVE en ce moment dans cette salle ? */
    const active = reservations.find(r =>
      r.salle === room.name &&
      r.date  === today     &&
      r.debut <= now        &&
      r.fin   >= now
    );

    /* Y a-t-il une réservation à VENIR aujourd'hui ? */
    const upcoming = reservations.find(r =>
      r.salle === room.name &&
      r.date  === today     &&
      r.debut  > now
    );

    /* Détermine le statut visuel à afficher */
    let status   = 'Disponible';
    let dotColor = 'var(--accent)';   /* vert par défaut */

    if (active && active.statut === 'Occupé') {
      status   = 'Occupé';
      dotColor = 'var(--danger)';     /* rouge */
    } else if (active?.statut === 'Réservé' || upcoming) {
      status   = 'Réservé';
      dotColor = 'var(--warning)';    /* orange */
    }

    /* Construction de la carte */
    const div = document.createElement('div');
    div.className = 'room-card';
    div.innerHTML = `
      <span class="room-big-emoji">${room.emoji}</span>
      <div class="room-name">${room.name}</div>
      <div class="room-status-text">
        <span class="room-status-dot" style="background: ${dotColor}"></span>
        ${status}
      </div>
    `;

    /* Clic sur une carte = pré-sélectionne la salle dans le formulaire rapide */
    div.onclick = () => {
      document.getElementById('quickSalle').value = room.name;
    };

    grid.appendChild(div);
  });
}


/* ─── FONCTIONS UTILITAIRES ─────────────────────────────────
   Petites fonctions appelées souvent dans le code.
   ─────────────────────────────────────────────────────────── */

/* Transforme "2026-03-19" en "19/03/2026" (format français) */
function formatDate(d) {
  if (!d) return '—';
  const [year, month, day] = d.split('-');
  return `${day}/${month}/${year}`;
}

/* Retourne l'emoji associé à une salle */
function roomEmoji(salle) {
  const found = ROOMS.find(r => r.name === salle);
  return found ? found.emoji : '📍';
}

/* Retourne la classe CSS du badge selon le statut */
function statusClass(statut) {
  if (statut === 'Disponible') return 'available';
  if (statut === 'Occupé')     return 'occupied';
  return 'reserved';
}


/* ─── DÉTECTION DE CONFLIT ──────────────────────────────────
   Deux réservations sont en conflit si :
     - même salle ET même date
     - ET leurs créneaux horaires se chevauchent
   La formule (debut1 < fin2 && fin1 > debut2) est la façon
   standard de détecter un chevauchement d'intervalles.
   ─────────────────────────────────────────────────────────── */
function hasConflict(salle, date, debut, fin, excludeId = null) {
  return reservations.some(r => {
    if (r.id    === excludeId) return false;   /* on ignore la résa qu'on modifie */
    if (r.salle !== salle)     return false;
    if (r.date  !== date)      return false;
    return debut < r.fin && fin > r.debut;     /* chevauchement ? */
  });
}


/* ─── FORMULAIRE RAPIDE (SIDEBAR) ───────────────────────────
   On écoute les changements sur les 4 champs pour déclencher
   la vérification de conflit en temps réel.
   ─────────────────────────────────────────────────────────── */
document.getElementById('quickDate').addEventListener('change',  checkQuickConflict);
document.getElementById('quickSalle').addEventListener('change', checkQuickConflict);
document.getElementById('quickStart').addEventListener('change', checkQuickConflict);
document.getElementById('quickEnd').addEventListener('change',   checkQuickConflict);

function checkQuickConflict() {
  const salle = document.getElementById('quickSalle').value;
  const date  = document.getElementById('quickDate').value;
  const debut = document.getElementById('quickStart').value;
  const fin   = document.getElementById('quickEnd').value;

  const warning = document.getElementById('conflictWarning');

  /* Affiche ou cache l'avertissement selon qu'il y a un conflit */
  if (salle && date && debut && fin && hasConflict(salle, date, debut, fin)) {
    warning.classList.add('show');
  } else {
    warning.classList.remove('show');
  }
}

/* Valide et enregistre la réservation depuis le formulaire rapide */
function addQuickReservation() {
  const date  = document.getElementById('quickDate').value;
  const profil = document.getElementById('quickProfil').value;
  const salle = document.getElementById('quickSalle').value;
  const debut = document.getElementById('quickStart').value;
  const fin   = document.getElementById('quickEnd').value;

  /* Validation basique : tous les champs doivent être remplis */
  if (!date || !profil || !salle || !debut || !fin) {
    alert('Veuillez remplir tous les champs.');
    return;
  }

  if (fin <= debut) {
    alert("L'heure de fin doit être après l'heure de début.");
    return;
  }

  /* Ajout dans le tableau de données */
  reservations.push({ id: nextId++, date, profil, salle, statut: 'Réservé', debut, fin });

  clearQuickForm();
  render();
}

/* Réinitialise le formulaire rapide */
function clearQuickForm() {
  ['quickDate', 'quickProfil', 'quickSalle', 'quickStart', 'quickEnd'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('conflictWarning').classList.remove('show');
}


/* ─── MODAL : NOUVELLE RÉSERVATION ─────────────────────────
   Ouvre la fenêtre en mode "ajout" (formulaire vide).
   ─────────────────────────────────────────────────────────── */
function openAddModal() {
  editingId = null;

  document.getElementById('modalTitle').textContent = 'Nouvelle réservation';
  document.getElementById('compareSection').style.display = 'none';

  /* Vide tous les champs */
  document.getElementById('modalDate').value   = '';
  document.getElementById('modalProfil').value = '';
  document.getElementById('modalSalle').value  = '';
  document.getElementById('modalStatut').value = 'Réservé';
  document.getElementById('modalStart').value  = '';
  document.getElementById('modalEnd').value    = '';

  document.getElementById('modalOverlay').classList.add('open');
}


/* ─── MODAL : MODIFICATION ──────────────────────────────────
   Ouvre la fenêtre en mode "édition" avec les données
   existantes pré-remplies et le bloc Avant/Après visible.
   ─────────────────────────────────────────────────────────── */
function openEditModal(id) {
  editingId = id;

  const r = reservations.find(x => x.id === id);
  if (!r) return;

  document.getElementById('modalTitle').textContent = 'Modifier la réservation';

  /* Affiche le bloc "Avant" avec les valeurs actuelles */
  document.getElementById('compareSection').style.display = 'grid';
  document.getElementById('compareBefore').innerHTML = `
    📅 ${formatDate(r.date)}<br>
    👤 ${r.profil}<br>
    📍 ${roomEmoji(r.salle)} ${r.salle}<br>
    🕐 ${r.debut} → ${r.fin}
  `;

  /* Pré-remplit le formulaire */
  document.getElementById('modalDate').value   = r.date;
  document.getElementById('modalProfil').value = r.profil;
  document.getElementById('modalSalle').value  = r.salle;
  document.getElementById('modalStatut').value = r.statut;
  document.getElementById('modalStart').value  = r.debut;
  document.getElementById('modalEnd').value    = r.fin;

  document.getElementById('modalOverlay').classList.add('open');
}


/* ─── MISE À JOUR DU BLOC "APRÈS" EN TEMPS RÉEL ────────────
   À chaque modification dans le formulaire modal, on met à
   jour l'aperçu "Après" pour que l'utilisateur voit
   directement les changements avant de confirmer.
   ─────────────────────────────────────────────────────────── */
['modalDate', 'modalProfil', 'modalSalle', 'modalStart', 'modalEnd'].forEach(id => {
  document.getElementById(id).addEventListener('change', updateCompareAfter);
});

function updateCompareAfter() {
  const date   = document.getElementById('modalDate').value;
  const profil = document.getElementById('modalProfil').value;
  const salle  = document.getElementById('modalSalle').value;
  const debut  = document.getElementById('modalStart').value;
  const fin    = document.getElementById('modalEnd').value;

  document.getElementById('compareAfter').innerHTML = `
    📅 ${formatDate(date)}<br>
    👤 ${profil}<br>
    📍 ${roomEmoji(salle)} ${salle}<br>
    🕐 ${debut} → ${fin}
  `;
}


/* ─── CONFIRMATION DE LA MODAL ──────────────────────────────
   Appelée quand l'utilisateur clique sur "Confirmer".
   Gère à la fois l'ajout et la modification.
   ─────────────────────────────────────────────────────────── */
function confirmModal() {
  const date   = document.getElementById('modalDate').value;
  const profil = document.getElementById('modalProfil').value;
  const salle  = document.getElementById('modalSalle').value;
  const statut = document.getElementById('modalStatut').value;
  const debut  = document.getElementById('modalStart').value;
  const fin    = document.getElementById('modalEnd').value;

  if (!date || !profil || !salle || !debut || !fin) {
    alert('Veuillez remplir tous les champs.');
    return;
  }

  if (fin <= debut) {
    alert("L'heure de fin doit être après l'heure de début.");
    return;
  }

  /* On prévient mais on laisse quand même confirmer */
  if (hasConflict(salle, date, debut, fin, editingId)) {
    const ok = confirm('⚠️ Un conflit a été détecté avec une réservation existante. Confirmer quand même ?');
    if (!ok) return;
  }

  if (editingId) {
    /* MODE MODIFICATION : on trouve l'index et on remplace l'objet */
    const index = reservations.findIndex(r => r.id === editingId);
    reservations[index] = { id: editingId, date, profil, salle, statut, debut, fin };
  } else {
    /* MODE AJOUT : on pousse un nouvel objet */
    reservations.push({ id: nextId++, date, profil, salle, statut, debut, fin });
  }

  closeModal();
  render();
}


/* ─── FERMETURE DE LA MODAL ─────────────────────────────────
   Deux façons de fermer : bouton ✕ ou clic sur l'overlay.
   ─────────────────────────────────────────────────────────── */
function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
  editingId = null;
}

/* Clic en dehors de la modal = fermeture */
document.getElementById('modalOverlay').addEventListener('click', function (e) {
  if (e.target === this) closeModal();
});


/* ─── SUPPRESSION ───────────────────────────────────────────
   filter() retourne un nouveau tableau sans l'élément ciblé.
   On réassigne reservations avec ce nouveau tableau.
   ─────────────────────────────────────────────────────────── */
function deleteReservation(id) {
  const ok = confirm('Supprimer cette réservation ?');
  if (!ok) return;

  reservations = reservations.filter(r => r.id !== id);
  render();
}


/* ─── INITIALISATION ────────────────────────────────────────
   Au chargement de la page :
   - on met la date du jour dans le champ "quickDate"
   - on lance un premier rendu
   ─────────────────────────────────────────────────────────── */
const todayDate = new Date().toISOString().split('T')[0];
document.getElementById('quickDate').value = todayDate;

render();