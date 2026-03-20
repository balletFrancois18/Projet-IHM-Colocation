from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Depense, User
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
@login_required
def liste_depenses():
    user_id = session['user_id']
    user    = User.query.get(user_id)

    # Toutes les dépenses de tout le monde
    toutes = Depense.query.all()
    total  = sum(d.montant for d in toutes)

    # Dépenses de l'utilisateur connecté par catégorie
    mes_depenses = {}
    for cat in CATEGORIES:
        ma_dep = Depense.query.filter_by(
            user_id=user_id, categorie=cat
        ).first()
        mes_depenses[cat] = ma_dep.montant if ma_dep else 0

    # Barres par catégorie
    par_categorie = {}
    for cat in CATEGORIES:
        deps_cat  = [d for d in toutes if d.categorie == cat]
        total_cat = sum(d.montant for d in deps_cat)

        par_personne = {}
        for d in deps_cat:
            if d.payeur not in par_personne:
                par_personne[d.payeur] = 0
            par_personne[d.payeur] += d.montant

        barres = []
        for personne, montant in par_personne.items():
            pct = (montant / total_cat * 100) if total_cat > 0 else 0
            barres.append({
                'nom':         personne,
                'montant':     montant,
                'pourcentage': round(pct, 1),
                'couleur':     COULEURS.get(personne, '#888')
            })

        par_categorie[cat] = {
            'total':  total_cat,
            'barres': barres
        }

    return render_template('depenses.html',
                           user=user,
                           total=total,
                           mes_depenses=mes_depenses,
                           par_categorie=par_categorie,
                           couleurs=COULEURS)

@depenses_bp.route('/depenses/sauvegarder', methods=['POST'])
@login_required
def sauvegarder():
    user_id = session['user_id']
    user    = User.query.get(user_id)

    for cat in CATEGORIES:
        montant_str = request.form.get(cat, '0')
        montant     = float(montant_str) if montant_str else 0

        # Cherche si une dépense existe déjà
        existante = Depense.query.filter_by(
            user_id=user_id, categorie=cat
        ).first()

        if existante:
            existante.montant = montant
        else:
            if montant > 0:
                nouvelle = Depense(
                    titre     = cat,
                    montant   = montant,
                    payeur    = user.prenom,
                    categorie = cat,
                    user_id   = user_id
                )
                db.session.add(nouvelle)

    db.session.commit()
    return redirect(url_for('depenses.liste_depenses'))