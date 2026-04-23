from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from models import db, Reservation, User
from routes.auth import login_required
from datetime import date as today_date

reservations_bp = Blueprint('reservations', __name__)

ESPACES = [
    'Cuisine',
    'Salon',
    'Salle de bain',
    'Machine à laver',
    'Voiture',
    'Trottinette',
    'Vélos',
    'Télévision',
]

PALETTE = ['#F59E0B', '#5B6CFF', '#34D399', '#A78BFA', '#FF7A59', '#F87171', '#60A5FA']

def build_context(current_user_id):
    today = str(today_date.today())
    reservations = Reservation.query.order_by(
        Reservation.date, Reservation.heure_debut
    ).all()
    reservations_actives = {}
    for r in reservations:
        if r.date >= today and r.espace not in reservations_actives:
            reservations_actives[r.espace] = r
    # Couleurs identiques à la page dépenses : tri alphabétique sur prénoms + historiques
    from models import Depense
    prenoms_users = {u.prenom for u in User.query.all()}
    prenoms_historiques = {d.payeur for d in Depense.query.all() if d.payeur and d.payeur != 'none'}
    tous_prenoms = sorted({p.lower() for p in (prenoms_users | prenoms_historiques)})
    couleurs_users = {p: PALETTE[i % len(PALETTE)] for i, p in enumerate(tous_prenoms)}
    for p in list(prenoms_users | prenoms_historiques):
        couleurs_users.setdefault(p, couleurs_users.get(p.lower(), PALETTE[0]))
    # Mapping uid → couleur pour le template (qui utilise r.user_id ou r.profil)
    couleurs = {}
    for r in reservations:
        uid = r.user_id if r.user_id is not None else r.profil
        if uid not in couleurs:
            couleurs[uid] = couleurs_users.get(r.profil, PALETTE[0])
    return dict(espaces=ESPACES, reservations=reservations,
                reservations_actives=reservations_actives,
                couleurs=couleurs, couleurs_users=couleurs_users, today=today)

@reservations_bp.route('/reservations')
def liste_reservations():
    ctx = build_context(session.get('user_id'))
    return render_template('reservations.html', **ctx)

@reservations_bp.route('/reservations/ajouter', methods=['POST'])
@login_required
def ajouter_reservation():
    # Priorité à espace_final (gère le cas "Autre espace")
    espace      = request.form.get('espace_final') or request.form.get('espace')
    date        = request.form.get('date')
    heure_debut = request.form.get('heure_debut')
    heure_fin   = request.form.get('heure_fin')
    type_event  = request.form.get('type_event', '')

    # Bloque si la date est dans le passé
    if date and date < str(today_date.today()):
        flash("date_passee_resa", 'error_date_passee')
        return redirect(url_for('reservations.liste_reservations'))

    # Vérifie conflit sur le créneau (comparaison en minutes pour gérer minuit "00:00")
    def to_minutes(t):
        if not t:
            return None
        h, m = map(int, t.split(':'))
        # 00:00 en tant que fin de créneau = minuit = 1440 min
        return (h * 60 + m) or 1440

    conflit = None
    existantes = Reservation.query.filter_by(espace=espace, date=date).all()
    if heure_debut:
        new_start = to_minutes(heure_debut)
        new_end   = to_minutes(heure_fin) if heure_fin else None
        for ex in existantes:
            ex_start = to_minutes(ex.heure_debut)
            ex_end   = to_minutes(ex.heure_fin) if ex.heure_fin else None
            if ex_start is None:
                continue
            # Même heure de début = conflit direct
            if ex_start == new_start:
                conflit = ex
                break
            # Chevauchement d'intervalles si les deux ont une heure de fin
            if new_end and ex_end:
                if new_start < ex_end and ex_start < new_end:
                    conflit = ex
                    break

    if conflit:
        flash("Créneau déjà réservé pour cet espace.", 'error')
    else:
        nouvelle = Reservation(
            espace      = espace,
            date        = date,
            heure_debut = heure_debut,
            heure_fin   = heure_fin,
            statut      = 'confirmé',
            type_event  = type_event,
            profil      = session.get('user_prenom', 'Inconnu'),
            user_id     = session.get('user_id')
        )
        db.session.add(nouvelle)
        db.session.commit()
        flash("Réservation ajoutée avec succès.", 'success')

    return redirect(url_for('reservations.liste_reservations'))

@reservations_bp.route('/reservations/supprimer/<int:id>', methods=['POST'])
@login_required
def supprimer_reservation(id):
    r = Reservation.query.get_or_404(id)
    if r.user_id == session.get('user_id'):
        db.session.delete(r)
        db.session.commit()
        flash("Réservation supprimée.", 'success')
    else:
        flash("Vous ne pouvez pas supprimer la réservation de quelqu'un d'autre.", 'error')
    return redirect(url_for('reservations.liste_reservations'))


@reservations_bp.route('/reservations/modifier/<int:id>', methods=['POST'])
@login_required
def modifier_reservation(id):
    r = Reservation.query.get_or_404(id)
    if r.user_id == session.get('user_id'):
        r.espace = request.form.get('espace')
        r.date = request.form.get('date')
        r.heure_debut = request.form.get('heure_debut')
        r.heure_fin = request.form.get('heure_fin')
        db.session.commit()
        flash("Réservation modifiée avec succès.", 'success')
    else:
        flash("Vous ne pouvez pas modifier la réservation de quelqu'un d'autre.", 'error')
    return redirect(url_for('reservations.liste_reservations'))