from flask import Blueprint, render_template, request, redirect, url_for
# importe les outils Flask nécessaires

from models import db, Depense
# importe la table Depense depuis models.py

depenses_bp = Blueprint('depenses', __name__)
# crée un "module" de routes indépendant
# Blueprint = façon de découper l'app en morceaux


@depenses_bp.route('/depenses')
def liste_depenses():
    return redirect(url_for('depenses.html'))

@depenses_bp.route('/depenses/ajouter', methods=['GET', 'POST'])
def ajouter_depense():
    if request.method == 'POST':
        titre   = request.form['']
        montant = float(request.form[''])
        payeur  = request.form['']
        nouvelle = Depense(titre=titre, montant=montant, payeur=payeur)
        db.session.add(nouvelle)
        db.session.commit()
        return redirect(url_for('depenses.liste_depenses'))
    return render_template('ajouter_depenses.html')