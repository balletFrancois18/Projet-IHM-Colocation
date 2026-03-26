from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Depense, User
from routes.auth import login_required

depenses_bp = Blueprint('depenses', __name__)

POT_TOTAL = 2800


PALETTE = ['#F59E0B', '#5B6CFF', '#34D399', '#A78BFA', '#FF7A59', '#F87171', '#60A5FA']


# Catégories de base toujours présentes
CATEGORIES_BASE = ['loyer', 'activite', 'courses']

#SQL / base de données classique (ORM type SQLAlchemy)
@depenses_bp.route('/depenses')
def liste_depenses():
    # 1. On récupère TOUS les utilisateurs de la BDD
    tous_les_utilisateurs = User.query.all()
    
    # 2. On récupère les prénoms valides (utilisateurs réels)
    prenoms_valides = {u.prenom for u in tous_les_utilisateurs}

    # 3. On récupère TOUTES les dépenses, en filtrant les payeurs orphelins
    # (payeur 'none' = placeholder de catégorie vide, on le garde)
    # (payeur inconnu = ancienne donnée sans compte, on l'exclut de l'affichage)
    toutes_depenses = Depense.query.all()
    depenses_reelles = [
        d for d in toutes_depenses
        if d.payeur == 'none' or d.payeur in prenoms_valides
    ]

    # 4. Génération dynamique des couleurs
    # On associe chaque prénom de la BDD à une couleur de la PALETTE
    couleurs_dynamiques = {
        u.prenom: PALETTE[i % len(PALETTE)]
        for i, u in enumerate(tous_les_utilisateurs)
    }

    # 5. Calculs pour l'affichage (uniquement sur les dépenses valides)
    total_depenses = sum(d.montant for d in depenses_reelles if d.payeur != 'none')
    reste = POT_TOTAL - total_depenses

    # 6. Gestion des catégories supplémentaires
    toutes_cats_bdd = {d.categorie for d in toutes_depenses}
    cats_extra = [c for c in toutes_cats_bdd if c not in CATEGORIES_BASE and c != 'none']

    return render_template('depenses.html',
                           depenses=depenses_reelles,
                           total=total_depenses,
                           reste=reste,
                           pot_total=POT_TOTAL,
                           couleurs=couleurs_dynamiques,
                           cats_extra=cats_extra,
                           categories_base=CATEGORIES_BASE)

@depenses_bp.route('/depenses/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_depense():
    if request.method == 'POST':
        titre     = request.form['titre']
        montant   = float(request.form['montant'])
        payeur    = request.form['payeur']
        categorie = request.form.get('categorie', 'courses')

        # ✅ CORRECTION : on vérifie que le payeur est bien un utilisateur existant en BDD
        utilisateur_valide = User.query.filter_by(prenom=payeur).first()
        if not utilisateur_valide:
            return redirect(url_for('depenses.liste_depenses'))

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



@depenses_bp.route('/depenses/nettoyer', methods=['POST'])
@login_required
def nettoyer_orphelins():
    tous_les_utilisateurs = User.query.all()
    prenoms_valides = {u.prenom for u in tous_les_utilisateurs}

    orphelines = Depense.query.filter(
        Depense.payeur != 'none',
        ~Depense.payeur.in_(prenoms_valides)
    ).all()

    for d in orphelines:
        db.session.delete(d)

    db.session.commit()
    return redirect(url_for('depenses.liste_depenses'))