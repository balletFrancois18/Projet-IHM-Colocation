from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    nom       = db.Column(db.String(50), nullable=False)
    prenom    = db.Column(db.String(50), nullable=False)
    email     = db.Column(db.String(100), unique=True, nullable=False)
    password  = db.Column(db.String(200), nullable=False)
    last_seen = db.Column(db.DateTime, nullable=True)
    avatar    = db.Column(db.String(200), nullable=True)

class Annonce(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    titre      = db.Column(db.String(150), nullable=False)
    categorie  = db.Column(db.String(20), default='info')   # urgent / info / rappel
    date       = db.Column(db.DateTime, default=datetime.utcnow)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    auteur     = db.Column(db.String(50), nullable=False, default='?')

class Depense(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    titre     = db.Column(db.String(100), nullable=False)
    montant   = db.Column(db.Float, nullable=False)
    payeur    = db.Column(db.String(50), nullable=False)
    categorie = db.Column(db.String(50), default='courses')
    date      = db.Column(db.DateTime, default=datetime.utcnow)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Tache(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    titre          = db.Column(db.String(100), nullable=False)
    assignee       = db.Column(db.String(50), nullable=False)
    faite          = db.Column(db.Boolean, default=False)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_echeance  = db.Column(db.Date, nullable=True)


class EspaceReservation(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    nom       = db.Column(db.String(50), unique=True, nullable=False)
    icone     = db.Column(db.String(10), default='📌')
    categorie = db.Column(db.String(50), default='Autre')


class Reservation(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    espace      = db.Column(db.String(50), nullable=False)
    date        = db.Column(db.String(20), nullable=False)
    heure_debut = db.Column(db.String(10), nullable=False)
    heure_fin   = db.Column(db.String(10), nullable=False)
    statut      = db.Column(db.String(20), default='confirmé')
    type_event  = db.Column(db.String(50), default='')
    profil      = db.Column(db.String(50), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)