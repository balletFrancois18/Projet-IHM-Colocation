from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User

auth_bp = Blueprint('auth', __name__)

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
        return redirect(url_for('index'))
    return render_template('inscription.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.password == request.form['password']:
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))