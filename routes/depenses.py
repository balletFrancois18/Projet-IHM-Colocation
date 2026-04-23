from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from models import db, Depense, User
from routes.auth import login_required

depenses_bp = Blueprint('depenses', __name__)

POT_TOTAL = 2800


PALETTE = ['#F59E0B', '#5B6CFF', '#34D399', '#A78BFA', '#FF7A59', '#F87171', '#60A5FA']


# Catégories de base toujours présentes
CATEGORIES_BASE = ['loyer', 'activite', 'courses']

# Métadonnées visuelles par catégorie (slug → icône lucide + classe couleur)
CAT_META = {
    'loyer':    {'icon': 'banknote',        'color': 'loyer'},
    'activite': {'icon': 'star',            'color': 'activite'},
    'courses':  {'icon': 'shopping-basket', 'color': 'courses'},
}

#SQL / base de données classique (ORM type SQLAlchemy)
@depenses_bp.route('/depenses')
def liste_depenses():
    from flask import session as flask_session

    # Créer les catégories de base uniquement si la BDD est complètement vide
    if not Depense.query.first():
        for base in CATEGORIES_BASE:
            db.session.add(Depense(titre=base, montant=0, payeur='none', categorie=base))
        db.session.commit()

    tous_les_utilisateurs = User.query.all()
    prenoms_valides = {u.prenom for u in tous_les_utilisateurs}
    toutes_depenses = Depense.query.all()
    payeurs_historiques = {d.payeur for d in toutes_depenses if d.payeur and d.payeur != 'none'}
    tous_prenoms = prenoms_valides | payeurs_historiques

    depenses_reelles = [
        d for d in toutes_depenses
        if d.payeur == 'none' or d.payeur in tous_prenoms
    ]

    tous_prenoms_tries = sorted({p.lower() for p in tous_prenoms})
    couleurs_dynamiques = {p: PALETTE[i % len(PALETTE)] for i, p in enumerate(tous_prenoms_tries)}
    for p in list(tous_prenoms):
        couleurs_dynamiques.setdefault(p, couleurs_dynamiques.get(p.lower(), PALETTE[0]))

    total_depenses = sum(d.montant for d in depenses_reelles if d.payeur != 'none')
    reste = POT_TOTAL - total_depenses

    # Toutes les catégories triées par l'id minimum de leurs dépenses (ordre stable même après renommage)
    from sqlalchemy import func
    cat_min_ids = db.session.query(Depense.categorie, func.min(Depense.id)) \
        .filter(Depense.categorie != 'none') \
        .group_by(Depense.categorie).all()
    cats_ordered = [c for c, _ in sorted(cat_min_ids, key=lambda x: x[1])]

    current_user = db.session.get(User, flask_session.get('user_id')) if flask_session.get('user_id') else None
    current_user_prenom = current_user.prenom if current_user else None

    return render_template('depenses.html',
                           depenses=depenses_reelles,
                           total=total_depenses,
                           reste=reste,
                           pot_total=POT_TOTAL,
                           couleurs=couleurs_dynamiques,
                           cats_ordered=cats_ordered,
                           cat_meta=CAT_META,
                           current_user_prenom=current_user_prenom)

@depenses_bp.route('/depenses/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_depense():
    if request.method == 'POST':
        titre     = request.form['titre']
        montant   = float(request.form['montant'])
        categorie = request.form.get('categorie', 'courses')

        # Payeur = utilisateur connecté uniquement
        user = db.session.get(User, session['user_id'])
        payeur = user.prenom

        nouvelle = Depense(titre=titre, montant=montant,
                           payeur=payeur, categorie=categorie)
        db.session.add(nouvelle)
        db.session.commit()
        flash("Dépense ajoutée avec succès.", 'success')
        return redirect(url_for('depenses.liste_depenses'))
    return redirect(url_for('depenses.liste_depenses'))


@depenses_bp.route('/depenses/supprimer/<int:id>', methods=['POST'])
@login_required
def supprimer_depense(id):
    depense = Depense.query.get_or_404(id)
    user = db.session.get(User, session['user_id'])
    if depense.payeur != user.prenom:
        flash("Vous ne pouvez pas supprimer la dépense de quelqu'un d'autre.", 'error')
    else:
        db.session.delete(depense)
        db.session.commit()
        flash("Dépense supprimée.", 'success')
    return redirect(url_for('depenses.liste_depenses'))


@depenses_bp.route('/depenses/modifier/<int:id>', methods=['POST'])
@login_required
def modifier_depense(id):
    depense = Depense.query.get_or_404(id)
    user = db.session.get(User, session['user_id'])
    if depense.payeur != user.prenom:
        flash("Vous ne pouvez pas modifier la dépense de quelqu'un d'autre.", 'error')
    else:
        depense.titre   = request.form['titre']
        depense.montant = float(request.form['montant'])
        depense.categorie = request.form.get('categorie', depense.categorie)
        db.session.commit()
        flash("Dépense modifiée avec succès.", 'success')
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
            flash(f"Catégorie « {categorie} » ajoutée.", 'success')
        else:
            flash(f"La catégorie « {categorie} » existe déjà.", 'error')
    return redirect(url_for('depenses.liste_depenses'))


@depenses_bp.route('/depenses/renommer-categorie/<categorie>', methods=['POST'])
@login_required
def renommer_categorie(categorie):
    nouveau_nom = request.form.get('nouveau_nom', '').strip().lower().replace(' ', '-')
    if not nouveau_nom:
        flash("Le nom ne peut pas être vide.", 'error')
        return redirect(url_for('depenses.liste_depenses'))
    existe = Depense.query.filter_by(categorie=nouveau_nom).first()
    if existe and nouveau_nom != categorie:
        flash(f"La catégorie « {nouveau_nom} » existe déjà.", 'error')
        return redirect(url_for('depenses.liste_depenses'))
    Depense.query.filter_by(categorie=categorie).update({'categorie': nouveau_nom})
    db.session.commit()
    flash(f"Catégorie renommée en « {nouveau_nom} ».", 'success')
    return redirect(url_for('depenses.liste_depenses'))


@depenses_bp.route('/depenses/supprimer-categorie/<categorie>', methods=['POST'])
@login_required
def supprimer_categorie(categorie):
    Depense.query.filter_by(categorie=categorie).delete()
    db.session.commit()
    flash(f"Catégorie « {categorie} » supprimée.", 'success')
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