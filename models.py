from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coloc.db'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    nom      = db.Column(db.String(50), nullable=False)
    prenom   = db.Column(db.String(50), nullable=False)
    email    = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Depense(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    titre   = db.Column(db.String(100), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    payeur  = db.Column(db.String(50), nullable=False)
    date    = db.Column(db.DateTime, default=datetime.utcnow)

class Tache(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    titre    = db.Column(db.String(100), nullable=False)
    assignee = db.Column(db.String(50), nullable=False)
    faite    = db.Column(db.Boolean, default=False)