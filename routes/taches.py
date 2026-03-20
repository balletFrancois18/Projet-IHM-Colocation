from flask import Blueprint, redirect, url_for, render_template
from models import db, Tache

taches_bp = Blueprint('taches', __name__)

@taches_bp.route('/taches')
def liste_taches():
    taches = Tache.query.all()
    return render_template('taches.html', taches=taches)

@taches_bp.route('/taches/<int:id>/cocher')
def cocher_tache(id):
    tache = Tache.query.get_or_404(id)
    tache.faite = not tache.faite
    db.session.commit()
    return redirect(url_for('index'))