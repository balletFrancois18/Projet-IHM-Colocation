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

@reservations_bp.route('/reservations')
def liste_reservations():
    today = str(today_date.today())
    reservations = Reservation.query.order_by(
        Reservation.date, Reservation.heure_debut
    ).all()

    # Une réservation active par espace (aujourd'hui ou dans le futur)
    reservations_actives = {}
    for r in reservations:
        if r.date >= today and r.espace not in reservations_actives:
            reservations_actives[r.espace] = r

    return render_template('reservations.html',
                           espaces=ESPACES,
                           reservations=reservations,
                           reservations_actives=reservations_actives)

@reservations_bp.route('/reservations/ajouter', methods=['POST'])
@login_required
def ajouter_reservation():
    espace      = request.form.get('espace')
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