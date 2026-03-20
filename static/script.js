

/* 
 global
 */

/* 
 fichier depense

 */

const COULEURS = [
  '#F59E0B', '#5B6CFF', '#34D399', '#FF7A59',
  '#A78BFA', '#EC4899', '#14B8A6', '#F97316'
];

// Données initiales depuis Flask
const donneesFlask = {{ depenses | tojson }};

// Structure des catégories
const categories = {
  loyer:    { participants: [] },
  activite: { participants: [] },
  courses:  { participants: [] }
};

// Remplir avec les données Flask si disponibles
donneesFlask.forEach(d => {
  const cat = d.categorie || 'courses';
  if (categories[cat]) {
    categories[cat].participants.push({
      nom: d.payeur,
      montant: d.montant
    });
  }
});

// Si pas de données Flask, mettre des exemples
if (categories.loyer.participants.length === 0) {
  categories.loyer.participants    = [{nom:'Simon', montant:400},{nom:'Lola', montant:400},{nom:'Dorian', montant:400}];
  categories.activite.participants = [{nom:'Simon', montant:50},{nom:'Lola', montant:80}];
  categories.courses.participants  = [];
}

let potCommun = {{ total }} || 2800;

// ─── RENDU DES BARRES ────────────────────────────────────────────

function rendreBarre(categorie) {
  const data  = categories[categorie];
  const barre = document.getElementById('barre-' + categorie);
  const legende = document.getElementById('legende-' + categorie);

  if (!barre || !legende) return;

  const total = data.participants.reduce((s, p) => s + p.montant, 0);

  barre.innerHTML   = '';
  legende.innerHTML = '';

  if (total === 0) {
    barre.style.background = '#E5E7EB';
    legende.innerHTML = '<span style="font-size:12px;color:#9CA3AF">Aucun participant</span>';
    return;
  }

  barre.style.background = 'transparent';

  data.participants.forEach((p, i) => {
    const pct     = (p.montant / total * 100).toFixed(1);
    const couleur = COULEURS[i % COULEURS.length];

    // Segment de barre
    const seg = document.createElement('div');
    seg.className = 'barre-segment';
    seg.style.width      = pct + '%';
    seg.style.background = couleur;

    // Tooltip au survol
    const tip = document.createElement('div');
    tip.className   = 'tooltip';
    tip.textContent = p.nom + ' — ' + p.montant + ' €';
    seg.appendChild(tip);

    // Arrondir les coins
    if (i === 0) seg.style.borderRadius = '20px 0 0 20px';
    if (i === data.participants.length - 1) seg.style.borderRadius = '0 20px 20px 0';
    if (data.participants.length === 1) seg.style.borderRadius = '20px';

    barre.appendChild(seg);

    // Légende
    const item = document.createElement('div');
    item.className = 'legende-item';
    item.innerHTML = `
      <div class="legende-dot" style="background:${couleur}"></div>
      <span class="legende-nom">${p.nom}</span>
      <span>${p.montant} €</span>
    `;
    legende.appendChild(item);
  });
}

function rendreToutes() {
  ['loyer', 'activite', 'courses'].forEach(rendreBarre);
  mettreAJourTotal();
}

// ─── TOTAL POT COMMUN ────────────────────────────────────────────

function mettreAJourTotal() {
  document.getElementById('affichage-total').textContent = potCommun + ' €';
}

// ─── MODALS ──────────────────────────────────────────────────────

function ouvrirModalAjouter(categorie) {
  document.getElementById('modal-titre-participant').textContent = 'Ajouter un participant';
  document.getElementById('modal-categorie').value  = categorie;
  document.getElementById('modal-index-modifier').value = -1;
  document.getElementById('input-nom').value     = '';
  document.getElementById('input-montant').value = '';
  document.getElementById('modal-participant').classList.add('active');
  document.getElementById('input-nom').focus();
}

function ouvrirModalModifier(categorie) {
  const data = categories[categorie];
  if (data.participants.length === 0) {
    ouvrirModalAjouter(categorie);
    return;
  }
  // Modifier le dernier participant par défaut
  const idx = data.participants.length - 1;
  const p   = data.participants[idx];
  document.getElementById('modal-titre-participant').textContent = 'Modifier ' + p.nom;
  document.getElementById('modal-categorie').value  = categorie;
  document.getElementById('modal-index-modifier').value = idx;
  document.getElementById('input-nom').value     = p.nom;
  document.getElementById('input-montant').value = p.montant;
  document.getElementById('modal-participant').classList.add('active');
}

function validerParticipant() {
  const categorie = document.getElementById('modal-categorie').value;
  const idx       = parseInt(document.getElementById('modal-index-modifier').value);
  const nom       = document.getElementById('input-nom').value.trim();
  const montant   = parseFloat(document.getElementById('input-montant').value);

  if (!nom || isNaN(montant) || montant < 0) {
    alert('Remplis bien le nom et le montant !');
    return;
  }

  if (idx === -1) {
    // Ajouter
    categories[categorie].participants.push({ nom, montant });
  } else {
    // Modifier
    categories[categorie].participants[idx] = { nom, montant };
  }

  fermerModal('modal-participant');
  rendreBarre(categorie);
}

function ouvrirModalPot() {
  document.getElementById('input-pot').value = potCommun;
  document.getElementById('modal-pot').classList.add('active');
  document.getElementById('input-pot').focus();
  document.getElementById('input-pot').select();
}

function validerPot() {
  const val = parseFloat(document.getElementById('input-pot').value);
  if (!isNaN(val) && val >= 0) {
    potCommun = val;
    mettreAJourTotal();
  }
  fermerModal('modal-pot');
}

function fermerModal(id) {
  document.getElementById(id).classList.remove('active');
}

// Fermer en cliquant dehors
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', function(e) {
    if (e.target === this) this.classList.remove('active');
  });
});

// Entrée = valider
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
  }
});

// ─── ARTICLES COURSES ────────────────────────────────────────────

function ajouterArticle() {
  const input = document.getElementById('input-courses');
  const val   = input.value.trim();
  if (!val) return;

  const tag = document.createElement('span');
  tag.style.cssText = `
    background:#EEF2FF; color:#5B6CFF; padding:4px 12px;
    border-radius:20px; font-size:12px; font-weight:600;
    display:inline-flex; align-items:center; gap:6px;
  `;
  tag.innerHTML = val + ' <span style="cursor:pointer;opacity:0.6" onclick="this.parentElement.remove()">✕</span>';
  document.getElementById('liste-articles').appendChild(tag);
  input.value = '';
  input.focus();
}

document.getElementById('input-courses').addEventListener('keydown', e => {
  if (e.key === 'Enter') ajouterArticle();
});

// ─── INIT ─────────────────────────────────────────────────────────
rendreToutes();