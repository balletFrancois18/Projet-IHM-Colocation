from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Depense
from routes.auth import login_required

depenses_bp = Blueprint('depenses', __name__)

COULEURS = {
    'Banu':     '#5B6CFF',
    'Eoghan':   '#FF7A59',
    'Francois': '#34D399',
    'Loucia':   '#A78BFA',
    'Nassim':   '#F59E0B',
}


CATEGORIES = ['loyer', 'activite', 'courses', 'autres']

@depenses_bp.route('/depenses')
def liste_depenses():
    depenses = Depense.query.all()
    total    = sum(d.montant for d in depenses)

    par_categorie = {}
    for cat in CATEGORIES:
        deps_cat  = [d for d in depenses if d.categorie == cat]
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
                'couleur':     COULEURS.get(personne, '#888888')
            })

        par_categorie[cat] = {
            'depenses': deps_cat,
            'total':    total_cat,
            'barres':   barres
        }

    return render_template('depenses.html',
                           depenses=depenses,
                           total=total,
                           par_categorie=par_categorie,
                           couleurs=COULEURS)




@depenses_bp.route('/depenses')
def liste_depenses():
    depenses = Depense.query.all()
    total    = sum(d.montant for d in depenses)

    par_personne = {}
    for d in depenses:
        if d.payeur not in par_personne:
            par_personne[d.payeur] = 0
        par_personne[d.payeur] += d.montant

    barres = []
    for personne, montant in par_personne.items():
        pourcentage = (montant / total * 100) if total > 0 else 0
        barres.append({
            'nom':         personne,
            'montant':     montant,
            'pourcentage': round(pourcentage, 1),
            'couleur':     COULEURS.get(personne, '#888888')
        })

    return render_template('depenses.html',
                           depenses=depenses,
                           total=total,
                           barres=barres,
                           couleurs=COULEURS)


@depenses_bp.route('/depenses/supprimer/<int:id>')
def supprimer_depense(id):
    depense = Depense.query.get_or_404(id)
    db.session.delete(depense)
    db.session.commit()
    return redirect(url_for('depenses.liste_depenses'))

@depenses_bp.route('/depenses/modifier/<int:id>', methods=['POST'])
def modifier_depense(id):
    depense         = Depense.query.get_or_404(id)
    depense.titre   = request.form['titre']
    depense.montant = float(request.form['montant'])
    depense.payeur  = request.form['payeur']
    db.session.commit()
    return redirect(url_for('depenses.liste_depenses'))