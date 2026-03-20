from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Depense
from routes.auth import login_required

depenses_bp = Blueprint('depenses', __name__)

COULEURS = {
    'Banu':     '#F59E0B',
    'Eoghan':   '#5B6CFF',
    'Francois': '#34D399',
    'Loucia':   '#A78BFA',
    'Nassim':   '#FF7A59',
}

@depenses_bp.route('/depenses/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_depense():
    if request.method == 'POST':
        titre     = request.form['titre']
        montant   = float(request.form['montant'])
        payeur    = request.form['payeur']
        categorie = request.form.get('categorie', 'courses')
        nouvelle  = Depense(titre=titre, montant=montant,
                            payeur=payeur, categorie=categorie)
        db.session.add(nouvelle)
        db.session.commit()
        return redirect(url_for('depenses.liste_depenses'))  # ← redirige vers liste
    return render_template('depenses.html',
                           depenses=Depense.query.all(),
                           total=0,
                           couleurs=COULEURS)


@depenses_bp.route('/depenses')
def liste_depenses():
    depenses = Depense.query.all()
    total    = sum(d.montant for d in depenses)  # ← recalcule tout
    return render_template('depenses.html',
                           depenses=depenses,
                           total=total,
                           couleurs=COULEURS)











<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>CoLoc — Dépenses</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Syne:wght@700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'DM Sans', sans-serif; background: #F6F8FC; color: #111827; }

    .navbar {
      display: flex; align-items: center; justify-content: space-between;
      padding: 14px 32px; background: white; border-bottom: 1px solid #E5E7EB;
      position: sticky; top: 0; z-index: 50;
    }
    .nav-logo { font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800; }
    .nav-logo span { color: #5B6CFF; }
    .nav-links { display: flex; gap: 24px; }
    .nav-links a { text-decoration: none; color: #6B7280; font-weight: 500; font-size: 14px; }
    .nav-links a.active, .nav-links a:hover { color: #5B6CFF; }
    .nav-right { display: flex; gap: 10px; align-items: center; }
    .btn-ghost { padding: 8px 16px; border-radius: 10px; font-size: 13px; font-weight: 600; background: white; color: #6B7280; border: 1.5px solid #E5E7EB; text-decoration: none; }

    .container { max-width: 760px; margin: 40px auto; padding: 0 24px; }

    .pot-header {
      display: flex; align-items: center; justify-content: space-between;
      background: white; border-radius: 16px; padding: 20px 28px;
      margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    }
    .pot-label { font-size: 13px; color: #6B7280; margin-bottom: 4px; }
    .pot-montant { font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; color: #5B6CFF; }

    .categorie-card {
      background: white; border-radius: 16px; padding: 22px 26px;
      margin-bottom: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    }
    .cat-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
    .cat-titre { font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700; }
    .cat-actions { display: flex; gap: 8px; }
    .btn-round {
      width: 32px; height: 32px; border-radius: 50%;
      border: 1.5px solid #E5E7EB; background: white;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; font-size: 14px; color: #6B7280; transition: all 0.2s;
    }
    .btn-round:hover { border-color: #5B6CFF; color: #5B6CFF; }

    .barre {
      display: flex; height: 18px; border-radius: 20px;
      overflow: hidden; background: #E5E7EB; margin-bottom: 10px;
    }
    .barre-segment { height: 100%; position: relative; cursor: pointer; }
    .barre-segment:hover { filter: brightness(1.1); }
    .barre-segment .tooltip {
      position: absolute; bottom: calc(100% + 8px); left: 50%;
      transform: translateX(-50%); background: #1F2937; color: white;
      padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600;
      white-space: nowrap; opacity: 0; pointer-events: none;
      transition: opacity 0.2s; z-index: 10;
    }
    .barre-segment .tooltip::after {
      content: ''; position: absolute; top: 100%; left: 50%;
      transform: translateX(-50%); border: 5px solid transparent;
      border-top-color: #1F2937;
    }
    .barre-segment:hover .tooltip { opacity: 1; }

    .barre-legende { display: flex; gap: 14px; flex-wrap: wrap; }
    .legende-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #6B7280; }
    .legende-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
    .legende-nom { font-weight: 600; color: #111827; }

    .modal-overlay {
      display: none; position: fixed; inset: 0;
      background: rgba(0,0,0,0.35); z-index: 200;
      align-items: center; justify-content: center;
    }
    .modal-overlay.active { display: flex; }
    .modal {
      background: white; border-radius: 16px; padding: 28px; width: 360px;
      box-shadow: 0 16px 48px rgba(0,0,0,0.15); animation: slideUp 0.2s ease-out;
    }
    @keyframes slideUp { from { transform: translateY(16px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    .modal-titre { font-family: 'Syne', sans-serif; font-size: 17px; font-weight: 700; margin-bottom: 18px; }
    .field-group { margin-bottom: 12px; }
    .field-label { font-size: 11px; font-weight: 700; color: #6B7280; display: block; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
    .field-input { width: 100%; padding: 10px 12px; border: 1.5px solid #E5E7EB; border-radius: 8px; font-size: 13px; font-family: 'DM Sans', sans-serif; }
    .field-input:focus { outline: none; border-color: #5B6CFF; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }
    .btn-valider { padding: 9px 20px; background: #5B6CFF; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; font-family: 'DM Sans', sans-serif; }
    .btn-annuler { padding: 9px 16px; background: white; color: #6B7280; border: 1.5px solid #E5E7EB; border-radius: 8px; cursor: pointer; font-size: 13px; font-family: 'DM Sans', sans-serif; }
  </style>
</head>
<body>

<nav class="navbar">
  <div class="nav-logo">Co<span>Loc</span></div>
  <div class="nav-links">
    <a href="{{ url_for('index') }}">🏠 Accueil</a>
    <a href="{{ url_for('taches.liste_taches') }}">🧹 Tâches</a>
    <a href="{{ url_for('depenses.liste_depenses') }}" class="active">💸 Dépenses</a>
  </div>
  <div class="nav-right">
    <a href="{{ url_for('auth.logout') }}" class="btn-ghost">Déconnexion</a>
  </div>
</nav>

<div class="container">

  <!-- Pot commun — total calculé par Python -->
  <div class="pot-header">
    <div>
      <div class="pot-label">Montant Pot Commun</div>
      <div class="pot-montant">{{ total }} €</div>
    </div>
  </div>

  <!-- Loyer -->
  <div class="categorie-card">
    <div class="cat-header">
      <span class="cat-titre">🏠 Répartition loyer</span>
      <div class="cat-actions">
        <button class="btn-round" onclick="ouvrirModal('loyer')">＋</button>
      </div>
    </div>
    {% set deps = depenses | selectattr('categorie', 'equalto', 'loyer') | list %}
    {% set tot  = deps | sum(attribute='montant') %}
    <div class="barre">
      {% for d in deps %}
      <div class="barre-segment"
           style="width:{{ (d.montant/tot*100)|round(1) if tot > 0 else 0 }}%;background:{{ couleurs.get(d.payeur,'#888') }}">
        <div class="tooltip">{{ d.payeur }} — {{ d.montant }} €</div>
      </div>
      {% endfor %}
    </div>
    <div class="barre-legende">
      {% for d in deps %}
      <div class="legende-item">
        <div class="legende-dot" style="background:{{ couleurs.get(d.payeur,'#888') }}"></div>
        <span class="legende-nom">{{ d.payeur }}</span>
        <span>{{ d.montant }} €</span>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Activité -->
  <div class="categorie-card">
    <div class="cat-header">
      <span class="cat-titre">⚡ Activité principale</span>
      <div class="cat-actions">
        <button class="btn-round" onclick="ouvrirModal('activite')">＋</button>
      </div>
    </div>
    {% set deps = depenses | selectattr('categorie', 'equalto', 'activite') | list %}
    {% set tot  = deps | sum(attribute='montant') %}
    <div class="barre">
      {% for d in deps %}
      <div class="barre-segment"
           style="width:{{ (d.montant/tot*100)|round(1) if tot > 0 else 0 }}%;background:{{ couleurs.get(d.payeur,'#888') }}">
        <div class="tooltip">{{ d.payeur }} — {{ d.montant }} €</div>
      </div>
      {% endfor %}
    </div>
    <div class="barre-legende">
      {% for d in deps %}
      <div class="legende-item">
        <div class="legende-dot" style="background:{{ couleurs.get(d.payeur,'#888') }}"></div>
        <span class="legende-nom">{{ d.payeur }}</span>
        <span>{{ d.montant }} €</span>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Courses -->
  <div class="categorie-card">
    <div class="cat-header">
      <span class="cat-titre">🛒 Courses</span>
      <div class="cat-actions">
        <button class="btn-round" onclick="ouvrirModal('courses')">＋</button>
      </div>
    </div>
    {% set deps = depenses | selectattr('categorie', 'equalto', 'courses') | list %}
    {% set tot  = deps | sum(attribute='montant') %}
    <div class="barre">
      {% for d in deps %}
      <div class="barre-segment"
           style="width:{{ (d.montant/tot*100)|round(1) if tot > 0 else 0 }}%;background:{{ couleurs.get(d.payeur,'#888') }}">
        <div class="tooltip">{{ d.payeur }} — {{ d.montant }} €</div>
      </div>
      {% endfor %}
    </div>
    <div class="barre-legende">
      {% for d in deps %}
      <div class="legende-item">
        <div class="legende-dot" style="background:{{ couleurs.get(d.payeur,'#888') }}"></div>
        <span class="legende-nom">{{ d.payeur }}</span>
        <span>{{ d.montant }} €</span>
      </div>
      {% endfor %}
    </div>
  </div>

</div>

<!-- Modal ajouter -->
<div class="modal-overlay" id="modal">
  <div class="modal">
    <div class="modal-titre">Ajouter une dépense</div>
    <form method="POST" action="{{ url_for('depenses.ajouter_depense') }}">
      <input type="hidden" name="categorie" id="input-categorie">
      <div class="field-group">
        <label class="field-label">Titre</label>
        <input type="text" name="titre" class="field-input" placeholder="ex: Loyer mars" required>
      </div>
      <div class="field-group">
        <label class="field-label">Montant (€)</label>
        <input type="number" name="montant" class="field-input" placeholder="0" step="0.01" min="0" required>
      </div>
      <div class="field-group">
        <label class="field-label">Payeur</label>
        <select name="payeur" class="field-input">
          {% for nom in couleurs.keys() %}
          <option value="{{ nom }}">{{ nom }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn-annuler" onclick="fermerModal()">✕ Annuler</button>
        <button type="submit" class="btn-valider">✓ Valider</button>
      </div>
    </form>
  </div>
</div>

<script>
  function ouvrirModal(categorie) {
    document.getElementById('input-categorie').value = categorie;
    document.getElementById('modal').classList.add('active');
  }
  function fermerModal() {
    document.getElementById('modal').classList.remove('active');
  }
  document.getElementById('modal').addEventListener('click', function(e) {
    if (e.target === this) fermerModal();
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') fermerModal();
  });
</script>

</body>
</html>