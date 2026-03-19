from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # Lien vers les tâches et dépenses
    taches = db.relationship('Tache', backref='responsable', lazy=True)

class Depense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    montant = db.Column(db.Float, nullable=False) # C'est ici qu'on gère le pot commun [cite: 1, 12]
    payeur = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Tache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False) # ex: CUISINE, MÉNAGE [cite: 61, 62]
    assignee = db.Column(db.String(50), nullable=False)
    faite = db.Column(db.Boolean, default=False) # L'état X ou DONE [cite: 66, 73]
    score = db.Column(db.Integer, default=0) # Pour le "SCORE TOTAL" de votre maquette 

class Reservation(db.Model): # Pour la page 7 de vos schémas [cite: 79, 80]
    id = db.Column(db.Integer, primary_key=True)
    salle = db.Column(db.String(50), nullable=False) # SALLE DE BAIN, SALON [cite: 80]
    h_debut = db.Column(db.String(20), nullable=False)
    h_fin = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)