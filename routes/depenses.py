from flask import Blueprint, render_template, request, redirect, url_for
# importe les outils Flask nécessaires

from models import db, Depense
# importe la table Depense depuis models.py

from routes.auth import login_required
# importe le décorateur de protection de route depuis auth.py

depenses_bp = Blueprint('depenses', __name__)
# crée un "module" de routes indépendant
# Blueprint = façon de découper l'app en morceaux


# Couleur fixe par personne
couleurs = {
    'Banu':    '#5B6CFF',
    'Eoghan':    '#FF7A59',
    'Francois': '#34D399',
    'Loucia': '#34D399',
    'Nassim':    '#A78BFA',
}



@depenses_bp.route('/depenses')
def liste_depenses():
    depenses = Depense.query.all()
    total    = sum(d.montant for d in depenses)

    # Calcule combien chaque personne a dépensé
    par_personne = {}
    for d in depenses:
        if d.payeur not in par_personne:
            par_personne[d.payeur] = 0
        par_personne[d.payeur] += d.montant

    # Calcule le pourcentage de chaque personne
    barres = []
    for personne, montant in par_personne.items():
        pourcentage = (montant / total * 100) if total > 0 else 0
        barres.append({
            'nom':         personne,
            'montant':     montant,
            'pourcentage': round(pourcentage, 1),
            'couleur':     couleurs.get(personne, '#888888')
        })

    return render_template('depenses.html',
                           depenses=depenses,
                           total=total,
                           barres=barres)

@depenses_bp.route('/depenses/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_depense():
    if request.method == 'POST':
        titre   = request.form['titre']
        montant = float(request.form['montant'])
        payeur  = request.form['payeur']
        nouvelle = Depense(titre=titre, montant=montant, payeur=payeur)
        db.session.add(nouvelle)
        db.session.commit()
        return redirect(url_for('depenses.liste_depenses'))
    depenses = Depense.query.all()
    total    = sum(d.montant for d in depenses)
    return render_template('depenses.html',
                       depenses=depenses,
                       total=total,
                       barres=barres,
                       couleurs=couleurs) 

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