from flask import Flask, render_template
from flask_mail import Mail
from models import db, Tache, Depense
from routes.taches   import taches_bp
from routes.depenses import depenses_bp
from routes.auth     import auth_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coloc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'changeme'

app.config['MAIL_SERVER']        = 'smtp.gmail.com'
app.config['MAIL_PORT']          = 587
app.config['MAIL_USE_TLS']       = True
app.config['MAIL_USERNAME']      = 'ton.email@gmail.com'  # ← ton Gmail
app.config['MAIL_PASSWORD']      = 'abcdefghijklmnop'     # ← le code 16 caractères
app.config['MAIL_DEFAULT_SENDER'] = 'ton.email@gmail.com'

mail = Mail(app)
db.init_app(app)

app.register_blueprint(taches_bp)
app.register_blueprint(depenses_bp)
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    taches   = Tache.query.all()
    depenses = Depense.query.all()
    return render_template('index.html', taches=taches, depenses=depenses)

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
    seed_data()

if __name__ == '__main__':
    app.run(debug=True)



