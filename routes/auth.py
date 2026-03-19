from flask import Blueprint, flash, render_template, request, redirect, url_for, session
from models import db, User

auth_bp = Blueprint('auth', __name__)




#stocker les mdp
@auth_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        nouveau = User(
            nom     = request.form['nom'],
            prenom  = request.form['prenom'],
            email   = request.form['email'],
            password= request.form['password']
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
    return render_template('inscription.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))