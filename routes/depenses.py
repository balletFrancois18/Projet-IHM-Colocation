from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Depense

depenses_bp = Blueprint('depenses', __name__)

@depenses_bp.route('/depenses')
def liste_depenses():
    depenses = Depense.query.all()
    total = sum(d.montant for d in depenses)
    return render_template('depenses.html', depenses=depenses, total=total)

@depenses_bp.route('/depenses/ajouter', methods=['GET', 'POST'])
def ajouter_depense():
    if request.method == 'POST':
        titre   = request.form['titre']
        montant = float(request.form['montant'])
        payeur  = request.form['payeur']
        nouvelle = Depense(titre=titre, montant=montant, payeur=payeur)
        db.session.add(nouvelle)
        db.session.commit()
        return redirect(url_for('depenses.liste_depenses'))
    return render_template('depenses.html', depenses=Depense.query.all(), total=0)