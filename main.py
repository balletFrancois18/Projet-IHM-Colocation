from flask import Flask, render_template, session
from flask_mail import Mail
from models import db, Tache, Depense, Reservation, EspaceReservation, User, Annonce
from routes.taches   import taches_bp
from routes.depenses import depenses_bp
from routes.auth     import auth_bp
from routes.reservations import reservations_bp
from datetime import datetime
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coloc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'changeme'

app.config['MAIL_SERVER']        = 'smtp.gmail.com'
app.config['MAIL_PORT']          = 587
app.config['MAIL_USE_TLS']       = True
app.config['MAIL_USERNAME']      = 'banumathey5@gmail.com'  #email de l'expéditeur
app.config['MAIL_PASSWORD']      = 'zawp jcid nyoq purk' #mot de passe d'application
app.config['MAIL_DEFAULT_SENDER'] = 'banumathey5@gmail.com'

mail = Mail(app)

@app.before_request
def update_last_seen():
    if session.get('user_id'):
        user = db.session.get(User, session['user_id'])
        if user:
            user.last_seen = datetime.utcnow()
            db.session.commit()

db.init_app(app)

app.register_blueprint(taches_bp)
app.register_blueprint(depenses_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(reservations_bp)

@app.route('/')
def index():
    taches      = Tache.query.order_by(Tache.id.desc()).limit(5).all()
    depenses    = Depense.query.filter(Depense.payeur != 'none').order_by(Depense.id.desc()).limit(5).all()
    reservations = Reservation.query.all()

    # Palette couleur identique à la page dépenses (tri alphabétique sur prénoms + historiques)
    PALETTE = ['#F59E0B', '#5B6CFF', '#34D399', '#A78BFA', '#FF7A59', '#F87171', '#60A5FA']
    prenoms_users = {u.prenom for u in User.query.all()}
    prenoms_historiques = {d.payeur for d in Depense.query.all() if d.payeur and d.payeur != 'none'}
    tous_prenoms = sorted({p.lower() for p in (prenoms_users | prenoms_historiques)})
    couleurs_users = {p: PALETTE[i % len(PALETTE)] for i, p in enumerate(tous_prenoms)}
    # Ajouter aussi les variantes de casse pour les lookups
    for p in list(prenoms_users | prenoms_historiques):
        couleurs_users.setdefault(p, couleurs_users.get(p.lower(), PALETTE[0]))

    # Construire les événements du planning pour le JS
    planning_events = []
    for r in reservations:
        try:
            heure = int(r.heure_debut.split(':')[0])
        except Exception:
            heure = 9
        planning_events.append({
            'date':    r.date,
            'heure':   heure,
            'titre':   r.espace,
            'type':    'resa',
            'couleur': couleurs_users.get(r.profil, '#7bafd4'),
            'personne': r.profil
        })
    for t in Tache.query.filter_by(faite=False).all():
        if t.date_echeance:
            try:
                heure_t = int(t.heure_debut.split(':')[0]) if t.heure_debut else 9
            except Exception:
                heure_t = 9
            planning_events.append({
                'date':        t.date_echeance.isoformat(),
                'heure':       heure_t,
                'heure_debut': t.heure_debut or '',
                'heure_fin':   t.heure_fin or '',
                'titre':       t.titre,
                'type':        'tache',
                'couleur':     couleurs_users.get(t.assignee, '#f59e0b'),
                'personne':    t.assignee
            })

    utilisateurs = User.query.all()
    annonces = Annonce.query.order_by(Annonce.date.desc()).all()
    return render_template('index.html',
                           annonces=annonces,
                           taches=taches,
                           depenses=depenses,
                           utilisateurs=utilisateurs,
                           couleurs_users=couleurs_users,
                           now=datetime.utcnow(),
                           planning_events=json.dumps(planning_events))

def seed_data():
    if Tache.query.count() == 0:
        db.session.add_all([
            Tache(titre="Passer l'aspirateur", assignee="Lucas",     faite=True),
            Tache(titre="Sortir les poubelles", assignee="Marie",    faite=True),
            Tache(titre="Nettoyer la cuisine",  assignee="Thibault", faite=False),
            Tache(titre="Changer les draps",    assignee="Julie",    faite=False),
        ])
    if Depense.query.count() == 0:
        db.session.add_all([
            Depense(titre="Courses Monoprix", montant=57.0,  payeur="Marie"),
            Depense(titre="Facture EDF",       montant=90.0,  payeur="Thibault"),
            Depense(titre="Abonnement Fibre",  montant=39.99, payeur="Lucas"),
        ])
    db.session.commit()

with app.app_context():
    db.create_all()
    from sqlalchemy import text
    for col_sql in [
        'ALTER TABLE tache ADD COLUMN date_echeance DATE',
        'ALTER TABLE user ADD COLUMN last_seen DATETIME',
        'ALTER TABLE user ADD COLUMN avatar VARCHAR(200)',
        'CREATE TABLE IF NOT EXISTS annonce (id INTEGER PRIMARY KEY, titre VARCHAR(150) NOT NULL, categorie VARCHAR(20) DEFAULT "info", date DATETIME, user_id INTEGER REFERENCES user(id), auteur VARCHAR(50) NOT NULL DEFAULT "?")',
    ]:
        try:
            db.session.execute(text(col_sql))
            db.session.commit()
        except Exception:
            pass
    seed_data()

if __name__ == '__main__':
    app.run(debug=True)



