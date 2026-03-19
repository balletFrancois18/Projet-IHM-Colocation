from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coloc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # Lien vers les tâches et dépenses
    taches = db.relationship('Tache', backref='responsable', lazy=True) #backref pour faire le lien entre les tables

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
    faite    = db.Column(db.Boolean, default=False)
