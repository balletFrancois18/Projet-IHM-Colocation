from flask import Blueprint, render_template, request, redirect, url_for
# importe les outils Flask nécessaires

from models import db, Depense
# importe la table Depense depuis models.py

depenses_bp = Blueprint('depenses', __name__)
# crée un "module" de routes indépendant
# Blueprint = façon de découper l'app en morceaux


@depenses_bp.route('/depenses') #lit toutes les dépenses dans la BDD et calcule le total
def liste_depenses():
    depenses = Depense.query.all()
    total = sum(d.montant for d in depenses)
    return render_template('depenses.html', depenses=depenses, total=total)


 #affiche le formulaire d'ajout de dépense et la liste des dépenses existantes
@depenses_bp.route('/depenses/ajouter', methods=['GET', 'POST'])
def ajouter_depense():
    if request.method == 'POST': #enregistre dans la BDD et redirige vers la liste des dépenses
        titre   = request.form['titre']
        montant = float(request.form['montant'])
        payeur  = request.form['payeur']
        nouvelle = Depense(titre=titre, montant=montant, payeur=payeur)
        db.session.add(nouvelle)
        db.session.commit()
        return redirect(url_for('depenses.liste_depenses'))
    return render_template('depenses.html', depenses=Depense.query.all(), total=0)