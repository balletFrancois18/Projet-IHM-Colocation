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


# Catégories de base toujours présentes
CATEGORIES_BASE = ['loyer', 'activite', 'courses']

#SQL / base de données classique (ORM type SQLAlchemy)
@depenses_bp.route('/depenses')
def liste_depenses():
    depenses       = Depense.query.all()
    # Filtre les dépenses réelles (exclut les placeholders montant=0 payeur=none)
    depenses_reelles = [d for d in depenses if d.payeur != 'none']
    total_depenses   = sum(d.montant for d in depenses_reelles)
    reste            = POT_TOTAL - total_depenses

    # Récupère les catégories dynamiques depuis la BDD
    toutes_cats = {d.categorie for d in depenses}
    cats_extra  = [c for c in toutes_cats if c not in CATEGORIES_BASE]

    return render_template('depenses.html',
                           depenses=depenses_reelles,
                           total=total_depenses,
                           reste=reste,
                           pot_total=POT_TOTAL,
                           couleurs=COULEURS,
                           cats_extra=cats_extra)


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


@depenses_bp.route('/depenses/categorie/ajouter', methods=['POST'])
@login_required
def ajouter_categorie():
    categorie = request.form.get('categorie')
    if categorie:
        existe = Depense.query.filter_by(categorie=categorie).first()
        if not existe:
            placeholder = Depense(
                titre     = categorie,
                montant   = 0,
                payeur    = 'none',
                categorie = categorie
            )
            db.session.add(placeholder)
            db.session.commit()
    return redirect(url_for('depenses.liste_depenses'))



@depenses_bp.route('/depenses/supprimer-categorie/<categorie>', methods=['POST'])
@login_required
def supprimer_categorie(categorie):
    Depense.query.filter_by(categorie=categorie).delete()
    db.session.commit()
    return redirect(url_for('depenses.liste_depenses'))