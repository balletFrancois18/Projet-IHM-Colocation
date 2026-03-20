from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from flask_mail import Message
from models import db, User
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

# ── RÉSERVATIONS ──────────────────────────────
@auth_bp.route('/reservations')
def reservations():
    return render_template('reservations.html')