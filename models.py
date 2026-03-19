from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coloc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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

@app.route('/')
def index():
    taches   = Tache.query.all()
    depenses = Depense.query.all()
    return render_template('index.html', taches=taches, depenses=depenses)

@app.route('/taches')
def liste_taches():
    return redirect(url_for('index'))

@app.route('/depenses')
def liste_depenses():
    depenses = Depense.query.all()
    return render_template('index.html', taches=Tache.query.all(), depenses=depenses)

@app.route('/depenses/ajouter', methods=['GET', 'POST'])
def ajouter_depense():
    if request.method == 'POST':
        titre   = request.form['titre']
        montant = float(request.form['montant'])
        payeur  = request.form['payeur']
        nouvelle = Depense(titre=titre, montant=montant, payeur=payeur)
        db.session.add(nouvelle)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('ajouter_depense.html')

@app.route('/taches/<int:id>/cocher')
def cocher_tache(id):
    tache = Tache.query.get_or_404(id)
    tache.faite = not tache.faite
    db.session.commit()
    return redirect(url_for('index'))

def seed_data():
    if Tache.query.count() == 0:
        db.session.add_all([
            Tache(titre="Passer l'aspirateur", assignee="Lucas",    faite=True),
            Tache(titre="Sortir les poubelles", assignee="Marie",   faite=True),
            Tache(titre="Nettoyer la cuisine",  assignee="Thibault",faite=False),
            Tache(titre="Changer les draps",    assignee="Julie",   faite=False),
        ])
    if Depense.query.count() == 0:
        db.session.add_all([
            Depense(titre="Courses Monoprix",   montant=57.0,  payeur="Marie"),
            Depense(titre="Facture EDF",         montant=90.0,  payeur="Thibault"),
            Depense(titre="Abonnement Fibre",    montant=39.99, payeur="Lucas"),
        ])
    db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == '__main__':
    app.run(debug=True)