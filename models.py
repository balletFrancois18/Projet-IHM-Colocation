from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    nom      = db.Column(db.String(50), nullable=False)
    prenom   = db.Column(db.String(50), nullable=False)
    email    = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Depense(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    titre     = db.Column(db.String(100), nullable=False)
    montant   = db.Column(db.Float, nullable=False)
    payeur    = db.Column(db.String(50), nullable=False)
    categorie = db.Column(db.String(50), default='courses')
    date      = db.Column(db.DateTime, default=datetime.utcnow)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Tache(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    titre    = db.Column(db.String(100), nullable=False)
    assignee = db.Column(db.String(50), nullable=False)
    faite    = db.Column(db.Boolean, default=False)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)



    