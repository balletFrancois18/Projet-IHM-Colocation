from flask import Blueprint, render_template, request, redirect, url_for, jsonify
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

CATEGORIES = ['loyer', 'activite', 'courses']

@depenses_bp.route('/depenses')
def liste_depenses():
    depenses = Depense.query.all()
    total    = sum(d.montant for d in depenses)

    par_categorie = {}
    for cat in CATEGORIES:
        deps_cat  = [d for d in depenses if d.categorie == cat]
        total_cat = sum(d.montant for d in deps_cat)

        # Une ligne par personne dans cette catégorie
        par_personne = {}
        for d in deps_cat:
            if d.payeur not in par_personne:
                par_personne[d.payeur] = {'montant': 0, 'id': d.id}
            par_personne[d.payeur]['montant'] += d.montant

        barres = []
        for personne, data in par_personne.items():
            pct = (data['montant'] / total_cat * 100) if total_cat > 0 else 0
            barres.append({
                'nom':         personne,
                'montant':     data['montant'],
                'pourcentage': round(pct, 1),
                'couleur':     COULEURS.get(personne, '#888888')
            })

        par_categorie[cat] = {
            'total':  total_cat,
            'barres': barres
        }

    return render_template('depenses.html',
                           total=total,
                           par_categorie=par_categorie,
                           membres=list(COULEURS.keys()),
                           couleurs=COULEURS,
                           categories=CATEGORIES)

@depenses_bp.route('/depenses/maj', methods=['POST'])
@login_required
def maj_depense():
    data      = request.get_json()
    payeur    = data['payeur']
    categorie = data['categorie']
    montant   = float(data['montant'])

    # Cherche si une dépense existe déjà pour cette personne+catégorie
    existante = Depense.query.filter_by(
        payeur=payeur, categorie=categorie
    ).first()

    if existante:
        existante.montant = montant
    else:
        nouvelle = Depense(
            titre     = categorie,
            montant   = montant,
            payeur    = payeur,
            categorie = categorie
        )
        db.session.add(nouvelle)

    db.session.commit()
    return jsonify({'ok': True})

@depenses_bp.route('/depenses/total', methods=['POST'])
@login_required
def maj_total():
    # Le total est calculé automatiquement — cette route
    # permet juste de forcer un total fixe si besoin
    return jsonify({'ok': True})