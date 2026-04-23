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
    from datetime import date as date_type
    titre = request.form['titre']
    date_str = request.form.get('date_echeance', '').strip()
    date_echeance = None
    if date_str:
        try:
            date_echeance = date_type.fromisoformat(date_str)
        except ValueError:
            pass
    heure_debut = request.form.get('heure_debut', '').strip() or None
    heure_fin   = request.form.get('heure_fin', '').strip() or None
    user = db.session.get(User, session['user_id'])
    db.session.add(Tache(titre=titre, assignee=user.prenom, faite=False,
                         user_id=user.id, date_echeance=date_echeance,
                         heure_debut=heure_debut, heure_fin=heure_fin))
    db.session.commit()
    if date_echeance and date_echeance < date_type.today():
        flash("date_passee", 'warning_date_passee')
    else:
        flash("Tâche ajoutée avec succès.", 'success')
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
    flash("Tâche supprimée.", 'success')
    return redirect(url_for('taches.liste_taches'))


@taches_bp.route('/taches/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def modifier_tache(id):
    tache = db.get_or_404(Tache, id)
    if tache.user_id != session['user_id']:
        flash("Vous ne pouvez pas modifier la tâche de quelqu'un d'autre.", 'error')
        return redirect(url_for('taches.liste_taches'))
    if request.method == 'POST':
        tache.titre = request.form['titre']
        date_str = request.form.get('date_echeance', '').strip()
        if date_str:
            from datetime import date as date_type
            try:
                tache.date_echeance = date_type.fromisoformat(date_str)
            except ValueError:
                tache.date_echeance = None
        else:
            tache.date_echeance = None
        tache.heure_debut = request.form.get('heure_debut', '').strip() or None
        tache.heure_fin   = request.form.get('heure_fin', '').strip() or None
        db.session.commit()
        flash("Tâche modifiée avec succès.", 'success')
        return redirect(url_for('taches.liste_taches'))
    return render_template('taches.html', taches=Tache.query.all(), tache_modif=tache)
