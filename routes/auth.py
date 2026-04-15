from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from flask_mail import Message
from models import db, User, Tache, Depense, Reservation, Annonce
from functools import wraps
import secrets

auth_bp = Blueprint('auth', __name__)

# ── DÉCORATEUR login_required ─────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Connectez-vous pour accéder à cette page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# ── INSCRIPTION ───────────────────────────────
@auth_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        existant = User.query.filter_by(email=request.form['email']).first()
        if existant:
            flash('Cet email est déjà utilisé.', 'error')
            return render_template('inscription.html')
        nouveau = User(
            nom      = request.form['nom'],
            prenom   = request.form['prenom'],
            email    = request.form['email'],
            password = request.form['password']
        )
        db.session.add(nouveau)
        db.session.commit()
        flash('Compte créé avec succès ! Connectez-vous.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('inscription.html')

# ── LOGIN ─────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.password == request.form['password']:
            session['user_id']     = user.id
            session['user_prenom'] = user.prenom
            return redirect(url_for('index'))
        flash('Email ou mot de passe incorrect.', 'error')
    return render_template('login.html')

# ── LOGOUT ────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# ── RESET PASSWORD ────────────────────────────
@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        from main import mail
        email = request.form['email']
        user  = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(32)
            session['reset_token'] = token
            session['reset_email'] = email
            lien = url_for('auth.nouveau_mot_de_passe', token=token, _external=True)
            msg = Message(
                subject    = 'Réinitialisation de votre mot de passe — ColocApp',
                recipients = [email]
            )
            msg.body = (
                f"Bonjour {user.prenom},\n\n"
                f"Cliquez sur ce lien pour réinitialiser votre mot de passe :\n\n"
                f"{lien}\n\n"
                f"Ce lien est valable une seule fois.\n"
                f"Si vous n'avez pas demandé cette réinitialisation, ignorez cet email."
            )
            mail.send(msg)
        flash('Si cet email est enregistré, un lien vous a été envoyé.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html')

# ── NOUVEAU MOT DE PASSE ──────────────────────
@auth_bp.route('/nouveau_mot_de_passe/<token>', methods=['GET', 'POST'])
def nouveau_mot_de_passe(token):
    if token != session.get('reset_token'):
        flash('Lien invalide ou expiré.', 'error')
        return redirect(url_for('auth.reset_password'))
    if request.method == 'POST':
        email = session.get('reset_email')
        user  = User.query.filter_by(email=email).first()
        if user:
            user.password = request.form['new_password']
            db.session.commit()
            session.pop('reset_token', None)
            session.pop('reset_email', None)
            flash('Mot de passe modifié avec succès ! Connectez-vous.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('new_password.html', token=token)

# ── ANNONCES ─────────────────────────────────
@auth_bp.route('/annonces/ajouter', methods=['POST'])
@login_required
def ajouter_annonce():
    user = User.query.get(session['user_id'])
    annonce = Annonce(
        titre     = request.form['titre'].strip(),
        categorie = request.form.get('categorie', 'info'),
        auteur    = user.prenom,
        user_id   = user.id
    )
    db.session.add(annonce)
    db.session.commit()
    return redirect(url_for('index'))

@auth_bp.route('/annonces/supprimer/<int:id>', methods=['POST'])
@login_required
def supprimer_annonce(id):
    annonce = Annonce.query.get_or_404(id)
    if annonce.user_id == session['user_id']:
        db.session.delete(annonce)
        db.session.commit()
    return redirect(url_for('index'))

# ── PROFIL AVATAR ─────────────────────────────
@auth_bp.route('/profil/avatar', methods=['POST'])
@login_required
def upload_avatar():
    import os, uuid
    from werkzeug.utils import secure_filename
    f = request.files.get('avatar')
    if f and f.filename:
        ext = os.path.splitext(secure_filename(f.filename))[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
            flash('Format non supporté (jpg, png, gif, webp).', 'error')
            return redirect(url_for('auth.profil'))
        uploads = os.path.join('static', 'uploads')
        os.makedirs(uploads, exist_ok=True)
        nom = f'avatar_{session["user_id"]}_{uuid.uuid4().hex[:8]}{ext}'
        f.save(os.path.join(uploads, nom))
        user = User.query.get(session['user_id'])
        # Supprimer l'ancien avatar
        if user.avatar:
            ancien = os.path.join('static', 'uploads', user.avatar)
            if os.path.exists(ancien):
                os.remove(ancien)
        user.avatar = nom
        db.session.commit()
        flash('Photo de profil mise à jour.', 'success')
    return redirect(url_for('auth.profil'))

# ── RÉSERVATIONS ──────────────────────────────
@auth_bp.route('/reservations')
def reservations():
    from routes.reservations import build_context
    ctx = build_context(session.get('user_id'))
    return render_template('reservations.html', **ctx)

# ── PROFIL ────────────────────────────────────
@auth_bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_info':
            email_exists = User.query.filter(User.email == request.form['email'], User.id != user.id).first()
            if email_exists:
                flash('Cet email est déjà utilisé par un autre compte.', 'error')
            else:
                user.prenom = request.form['prenom']
                user.nom    = request.form['nom']
                user.email  = request.form['email']
                db.session.commit()
                session['user_prenom'] = user.prenom
                flash('Informations mises à jour avec succès.', 'success')
        elif action == 'update_password':
            if user.password != request.form['old_password']:
                flash('Mot de passe actuel incorrect.', 'error')
            elif request.form['new_password'] != request.form['confirm_password']:
                flash('Les nouveaux mots de passe ne correspondent pas.', 'error')
            else:
                user.password = request.form['new_password']
                db.session.commit()
                flash('Mot de passe modifié avec succès.', 'success')
        return redirect(url_for('auth.profil'))

    nb_taches      = Tache.query.filter_by(user_id=user.id).count()
    nb_depenses    = Depense.query.filter_by(user_id=user.id).count()
    nb_reservations = Reservation.query.filter_by(user_id=user.id).count()
    return render_template('profil.html', user=user,
                           nb_taches=nb_taches,
                           nb_depenses=nb_depenses,
                           nb_reservations=nb_reservations)