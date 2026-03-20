from flask import Blueprint, redirect, url_for
from models import db, Tache

taches_bp = Blueprint('taches', __name__)

@taches_bp.route('/taches')
def liste_taches():
    return redirect(url_for('taches.index'))

@taches_bp.route('/taches/<int:id>/cocher')
def cocher_tache(id):
    tache = Tache.query.get_or_404(id)
    tache.faite = not tache.faite
    db.session.commit()
    return redirect(url_for('index'))