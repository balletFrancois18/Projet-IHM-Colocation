from flask import Blueprint, redirect, url_for, render_template, request
from models import db, Tache
from routes.auth import login_required

taches_bp = Blueprint('taches', __name__)

@taches_bp.route('/taches')
def liste_taches():
    taches = Tache.query.all()
    return render_template('taches.html', taches=taches)

@taches_bp.route('/taches/<int:id>/cocher')
@login_required
def cocher_tache(id):
    tache = Tache.query.get_or_404(id)
    tache.faite = not tache.faite
    db.session.commit()
    return redirect(url_for('taches.liste_taches'))

@taches_bp.route('/taches/ajouter', methods=['POST'])
@login_required
def ajouter_tache():
    titre    = request.form['titre']
    assignee = request.form['assignee']
    nouvelle = Tache(titre=titre, assignee=assignee, faite=False)
    db.session.add(nouvelle)
    db.session.commit()
    return redirect(url_for('taches.liste_taches'))

    
@taches_bp.route('/taches/<int:id>/modifier', methods=['POST']) 
@login_required
def modifier_tache(id):
    tache = Tache.query.get_or_404(id)
    if request.method == 'POST':
        tache.titre = request.form['titre']
        tache.assignee = request.form['assignee']
        db.session.commit()
        # Vérifiez que 'taches.liste_taches' est bien le nom de votre route d'affichage
        return redirect(url_for('taches.liste_taches'))


#AJOUT FONCTIONNALITE SUPPRIMER TACHE
@taches_bp.route('/taches/<int:id>/supprimer', methods=['POST'])
@login_required
def supprimer_tache(id):
    tache = Tache.query.get_or_404(id)
    db.session.delete(tache)
    db.session.commit()
    return redirect(url_for('taches.liste_taches'))