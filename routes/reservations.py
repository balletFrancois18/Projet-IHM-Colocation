from flask import Blueprint, redirect, url_for, render_template, request
from models import db, Tache
from routes.auth import login_required

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/reservations')
def liste_reservations():
    reservations = Reservation.query.all()
    return render_template('reservations.html', reservations=reservations)

@reservations_bp.route('/reservations/<int:id>/cocher')
@login_required
def cocher_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    reservation.faite = not reservation.faite
    db.session.commit()
    return redirect(url_for('reservations.liste_reservations'))

@reservations_bp.route('/reservations/ajouter', methods=['POST'])
@login_required
def ajouter_reservation():
    titre    = request.form['titre']
    assignee = request.form['assignee']
    nouvelle = Reservation(titre=titre, assignee=assignee, faite=False)
    db.session.add(nouvelle)
    db.session.commit()
    return redirect(url_for('reservations.liste_reservations'))


#AJOUT FONCTIONNALITE SUPPRIMER TACHE
@reservations_bp.route('/reservations/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer_reservation(id):
    tache = Tache.query.get_or_404(id)
    db.session.delete(tache)
    db.session.commit()
    return redirect(url_for('reservations.liste_reservations'))