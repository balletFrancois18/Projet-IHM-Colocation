from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from flask_mail import Message
from models import db, User
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
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

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.password == request.form['password']:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash('Email ou mot de passe incorrect.', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        from main import mail
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Génère un token unique
            token = secrets.token_urlsafe(32)
            session['reset_token'] = token
            session['reset_email'] = email
            # Crée le lien avec le token
            lien = url_for('auth.nouveau_mot_de_passe', token=token, _external=True)
            # Envoie l'email
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
        # Message générique pour ne pas révéler si l'email existe
        flash('Si cet email est enregistré, un lien vous a été envoyé.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html')

@auth_bp.route('/nouveau_mot_de_passe/<token>', methods=['GET', 'POST'])
def nouveau_mot_de_passe(token):
    # Vérifie que le token est valide
    if token != session.get('reset_token'):
        flash('Lien invalide ou expiré.', 'error')
        return redirect(url_for('auth.reset_password'))
    if request.method == 'POST':
        email = session.get('reset_email')
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = request.form['new_password']
            db.session.commit()
            # Supprime le token pour qu'il ne soit plus utilisable
            session.pop('reset_token', None)
            session.pop('reset_email', None)
            flash('Mot de passe modifié avec succès ! Connectez-vous.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('new_password.html', token=token)