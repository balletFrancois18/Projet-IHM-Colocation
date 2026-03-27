from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from models import db, Tache, User
from routes.auth import login_required

taches_bp = Blueprint('taches', __name__)


@taches_bp.route('/taches')
def liste_taches():
    taches = Tache.query.all()
    return render_template('taches.html', taches=taches)


@taches_bp.route('/taches/ajouter', methods=['POST'])
@login_required
def ajouter_tache():
    titre = request.form['titre']
    user = db.session.get(User, session['user_id'])
    db.session.add(Tache(titre=titre, assignee=user.prenom, faite=False, user_id=user.id))
    db.session.commit()
    return redirect(url_for('taches.liste_taches'))


@taches_bp.route('/taches/<int:id>/cocher', methods=['POST'])
@login_required
def cocher_tache(id):
    tache = db.get_or_404(Tache, id)
    if tache.user_id != session['user_id']:
        flash("Vous ne pouvez pas modifier la tâche de quelqu'un d'autre.", 'error')
        return redirect(url_for('taches.liste_taches'))
    tache.faite = not tache.faite
    db.session.commit()
    return redirect(url_for('taches.liste_taches'))


@taches_bp.route('/taches/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer_tache(id):
    tache = db.get_or_404(Tache, id)
    if tache.user_id != session['user_id']:
        flash("Vous ne pouvez pas supprimer la tâche de quelqu'un d'autre.", 'error')
        return redirect(url_for('taches.liste_taches'))
    db.session.delete(tache)
    db.session.commit()
    return redirect(url_for('taches.liste_taches'))
