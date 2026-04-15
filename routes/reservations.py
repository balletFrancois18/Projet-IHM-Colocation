from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Reservation
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

PALETTE = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']

def build_context(current_user_id):
    today = str(today_date.today())
    reservations = Reservation.query.order_by(
        Reservation.date, Reservation.heure_debut
    ).all()
    reservations_actives = {}
    for r in reservations:
        if r.date >= today and r.espace not in reservations_actives:
            reservations_actives[r.espace] = r
    # Couleur fixe par user_id (le user connecté = bleu #3b82f6, les autres tournent sur la palette sans bleu)
    autres_palette = ['#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']
    couleurs = {}
    idx = 0
    for r in reservations:
        uid = r.user_id if r.user_id is not None else r.profil
        if uid not in couleurs:
            if uid == current_user_id:
                couleurs[uid] = '#3b82f6'
            else:
                couleurs[uid] = autres_palette[idx % len(autres_palette)]
                idx += 1
    return dict(espaces=ESPACES, reservations=reservations,
                reservations_actives=reservations_actives,
                couleurs=couleurs, today=today)

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

    # Vérifie conflit
    conflit = Reservation.query.filter_by(
        espace=espace, date=date
    ).filter(
        Reservation.heure_debut < heure_fin,
        Reservation.heure_fin   > heure_debut
    ).first()

    if not conflit:
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

    return redirect(url_for('reservations.liste_reservations'))

@reservations_bp.route('/reservations/supprimer/<int:id>', methods=['POST'])
@login_required
def supprimer_reservation(id):
    r = Reservation.query.get_or_404(id)
    if r.user_id == session.get('user_id'):
        db.session.delete(r)
        db.session.commit()
    return redirect(url_for('reservations.liste_reservations'))