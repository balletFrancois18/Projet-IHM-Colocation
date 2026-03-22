

/* 
 global
 */

/* 
 fichier depense

 */

// function ouvrirModalModifier(id, titre, montant, payeur) {
//   document.getElementById('modal-titre').textContent = 'Modifier une charge';
//   document.getElementById('modal-form').action = '/depenses/modifier/' + id;
//   document.getElementById('input-titre').value   = titre;
//   document.getElementById('input-montant').value = montant;
//   document.getElementById('input-payeur').value  = payeur;
//   document.getElementById('modal').classList.add('active');
// }

// function ouvrirModal(type) {
//   document.getElementById('modal-titre').textContent = 'Ajouter une charge';
//   document.getElementById('modal-form').action = "{{ url_for('depenses.ajouter_depense') }}";
//   document.getElementById('input-titre').value   = '';
//   document.getElementById('input-montant').value = '';
//   document.getElementById('input-payeur').value  = '';
//   document.getElementById('modal').classList.add('active');
// }

const donneesFlask = [
  {% for d in depenses %}
  { payeur: "{{ d.payeur }}", montant: {{ d.montant }}, categorie: "{{ d.categorie }}" }{% if not loop.last %},{% endif %}
  {% endfor %}
];

const COULEURS_MAP = {{ couleurs | tojson }};

const categories = {
  loyer:    { participants: [] },
  activite: { participants: [] },
  courses:  { participants: [] }
};

{% for cat in cats_extra %}
categories['{{ cat }}'] = { participants: [] };
{% endfor %}

donneesFlask.forEach(d => {
  const cat = d.categorie || 'courses';
  if (categories[cat]) {
    categories[cat].participants.push({
      nom:     d.payeur,
      montant: d.montant,
      couleur: COULEURS_MAP[d.payeur] || '#888888'
    });
  }
});

function rendreBarre(categorie) {
  const data    = categories[categorie];
  const barre   = document.getElementById('barre-' + categorie);
  const legende = document.getElementById('legende-' + categorie);
  if (!barre || !legende) return;

  const total = data.participants.reduce((s, p) => s + p.montant, 0);
  barre.innerHTML   = '';
  legende.innerHTML = '';

  if (total === 0) {
    barre.style.background = '#E5E7EB';
    legende.innerHTML = '<span style="font-size:12px;color:#9CA3AF">Aucune dépense</span>';
    return;
  }

  barre.style.background = 'transparent';

  data.participants.forEach((p, i) => {
    const pct = (p.montant / total * 100).toFixed(1);
    const seg = document.createElement('div');
    seg.className        = 'barre-segment';
    seg.style.width      = pct + '%';
    seg.style.background = p.couleur;
    if (i === 0) seg.style.borderRadius = '20px 0 0 20px';
    if (i === data.participants.length - 1) seg.style.borderRadius = '0 20px 20px 0';
    if (data.participants.length === 1) seg.style.borderRadius = '20px';

    const tip = document.createElement('div');
    tip.className   = 'tooltip';
    tip.textContent = p.nom + ' — ' + p.montant + ' €';
    seg.appendChild(tip);
    barre.appendChild(seg);

    const item = document.createElement('div');
    item.className = 'legende-item';
    item.innerHTML = `
      <div class="legende-dot" style="background:${p.couleur}"></div>
      <span class="legende-nom">${p.nom}</span>
      <span>${p.montant} €</span>
    `;
    legende.appendChild(item);
  });
}

function ouvrirModalAjouter(categorie) {
  document.getElementById('modal-titre-participant').textContent = 'Ajouter';
  document.getElementById('modal-categorie').value = categorie;
  document.getElementById('input-montant').value   = '';
  document.getElementById('modal-participant').classList.add('active');
}

function ouvrirModalModifier(categorie) {
  ouvrirModalAjouter(categorie);
}

function validerParticipant() {
  const categorie = document.getElementById('modal-categorie').value;
  const nom       = document.getElementById('input-nom').value;
  const montant   = parseFloat(document.getElementById('input-montant').value);

  if (!nom || isNaN(montant)) {
    alert('Remplis le nom et le montant !');
    return;
  }

  const form = document.createElement('form');
  form.method = 'POST';
  form.action = '/depenses/ajouter';

  [['titre', nom], ['montant', montant], ['payeur', nom], ['categorie', categorie]].forEach(([k, v]) => {
    const i = document.createElement('input');
    i.type = 'hidden'; i.name = k; i.value = v;
    form.appendChild(i);
  });

  document.body.appendChild(form);
  form.submit();
}

function supprimerCategorie(categorie) {
  if (!confirm('Supprimer toutes les dépenses de "' + categorie + '" ?')) return;

  const form = document.createElement('form');
  form.method = 'POST';
  form.action = '/depenses/supprimer-categorie/' + categorie;
  document.body.appendChild(form);
  form.submit();
}

function ouvrirModalPot() {
  document.getElementById('modal-pot').classList.add('active');
}

function validerPot() {
  fermerModal('modal-pot');
}

function fermerModal(id) {
  document.getElementById(id).classList.remove('active');
}

document.querySelectorAll('.modal-overlay').forEach(o => {
  o.addEventListener('click', function(e) {
    if (e.target === this) this.classList.remove('active');
  });
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape')
    document.querySelectorAll('.modal-overlay.active')
      .forEach(m => m.classList.remove('active'));
});

document.getElementById('input-courses').addEventListener('keydown', function(e) {
  if (e.key !== 'Enter') return;
  const val = this.value.trim();
  if (!val) return;
  const tag = document.createElement('span');
  tag.style.cssText = 'background:#EEF2FF;color:#5B6CFF;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;display:inline-flex;align-items:center;gap:6px;';
  tag.innerHTML = val + ' <span style="cursor:pointer;opacity:0.6" onclick="this.parentElement.remove()">✕</span>';
  document.getElementById('liste-articles').appendChild(tag);
  this.value = '';
});

function ouvrirModalNouvelleCategorie() {
  document.getElementById('input-nouvelle-cat').value = '';
  document.getElementById('modal-categorie-nouvelle').classList.add('active');
}

function ajouterNouvelleCategorie() {
  const nom = document.getElementById('input-nouvelle-cat').value.trim();
  if (!nom) { alert('Donne un nom !'); return; }

  const form = document.createElement('form');
  form.method = 'POST';
  form.action = '/depenses/categorie/ajouter';

  const input = document.createElement('input');
  input.type  = 'hidden';
  input.name  = 'categorie';
  input.value = nom.toLowerCase().replace(/\s+/g, '-');
  form.appendChild(input);

  document.body.appendChild(form);
  form.submit();
}

['loyer', 'activite', 'courses'].forEach(rendreBarre);
{% for cat in cats_extra %}
rendreBarre('{{ cat }}');
{% endfor %}

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


//tâches
  function ouvrirModalDepense(type) {
    document.getElementById('modal-titre').textContent = 'Ajouter une charge';
    document.getElementById('modal-form').action = '/depenses/ajouter';
    document.getElementById('input-titre').value   = '';
    document.getElementById('input-montant').value = '';
    document.getElementById('input-payeur').value  = '';
    document.getElementById('modal').classList.add('active');
  }

    function fermerModal() {
      document.getElementById('modal-overlay').classList.remove('active');
    }

    function fermerModalOverlay(e) {
      if (e.target === document.getElementById('modal-overlay')) fermerModal();
    }

    // Filtres
    function filtrer(statut, btn) {
      document.querySelectorAll('.filtre-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('.tache-card').forEach(card => {
        if (statut === 'tous' || card.dataset.statut === statut) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }