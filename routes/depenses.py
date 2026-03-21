from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Depense, User
from routes.auth import login_required

depenses_bp = Blueprint('depenses', __name__)

POT_TOTAL = 2800

COULEURS = {
    'Banu':     '#F59E0B',
    'Eoghan':   '#5B6CFF',
    'Francois': '#34D399',
    'Loucia':   '#A78BFA',
    'Nassim':   '#FF7A59',
}

@depenses_bp.route('/depenses')
def liste_depenses():
    depenses       = Depense.query.all()
    total_depenses = sum(d.montant for d in depenses)
    reste          = POT_TOTAL - total_depenses
    return render_template('depenses.html',
                           depenses=depenses,
                           total=total_depenses,
                           reste=reste,
                           pot_total=POT_TOTAL,
                           couleurs=COULEURS)

@depenses_bp.route('/depenses/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_depense():
    if request.method == 'POST':
        titre     = request.form['titre']
        montant   = float(request.form['montant'])
        payeur    = request.form['payeur']
        categorie = request.form.get('categorie', 'courses')

        existante = Depense.query.filter(
            db.func.lower(Depense.payeur) == payeur.lower(),
            Depense.categorie == categorie
        ).first()

        if existante:
            existante.montant = montant
            existante.payeur  = payeur
        else:
            nouvelle = Depense(titre=titre, montant=montant,
                               payeur=payeur, categorie=categorie)
            db.session.add(nouvelle)

        db.session.commit()
        return redirect(url_for('depenses.liste_depenses'))
    return redirect(url_for('depenses.liste_depenses'))