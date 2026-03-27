"""
Tests unitaires — routes/taches.py
Couvre :
  - Lecture de la liste (tout le monde)
  - Ajout d'une tâche (utilisateur connecté)
  - Cochage d'une tâche (propriétaire uniquement)
  - Suppression d'une tâche (propriétaire uniquement)
  - Refus d'action sur la tâche d'autrui
  - Redirection vers login si non connecté
"""
import pytest
from main import app
from models import db, User, Tache


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.drop_all()
        db.create_all()
        # Deux utilisateurs
        alice = User(nom='Dupont', prenom='Alice', email='alice@test.com', password='pass')
        bob   = User(nom='Martin', prenom='Bob',   email='bob@test.com',   password='pass')
        db.session.add_all([alice, bob])
        db.session.commit()

        # Tâche d'Alice (avec user_id)
        tache_alice = Tache(titre='Aspirateur', assignee='Alice', faite=False, user_id=alice.id)
        # Tâche sans propriétaire (données legacy / seed)
        tache_legacy = Tache(titre='Cuisine', assignee='Ancien', faite=False, user_id=None)
        db.session.add_all([tache_alice, tache_legacy])
        db.session.commit()

    with app.test_client() as c:
        yield c


def login_as(client, email, password='pass'):
    return client.post('/login', data={'email': email, 'password': password},
                       follow_redirects=True)


def login_as_alice(client):
    return login_as(client, 'alice@test.com')


def login_as_bob(client):
    return login_as(client, 'bob@test.com')


# ── 1. LISTE ──────────────────────────────────────────────────────────────────

class TestListeTaches:
    def test_liste_accessible_sans_login(self, client):
        """Tout le monde peut voir la liste des tâches."""
        r = client.get('/taches')
        assert r.status_code == 200

    def test_liste_contient_toutes_les_taches(self, client):
        r = client.get('/taches')
        data = r.data.decode()
        assert 'Aspirateur' in data
        assert 'Cuisine' in data

    def test_bouton_ajouter_absent_sans_login(self, client):
        """Le bouton '+ Ajouter une tâche' ne doit pas apparaître si non connecté."""
        r = client.get('/taches')
        assert b'ouvrirModal' not in r.data

    def test_bouton_ajouter_present_avec_login(self, client):
        login_as_alice(client)
        r = client.get('/taches')
        assert b'ouvrirModal' in r.data


# ── 2. AJOUTER ────────────────────────────────────────────────────────────────

class TestAjouterTache:
    def test_ajouter_redirige_vers_login_si_non_connecte(self, client):
        r = client.post('/taches/ajouter', data={'titre': 'Test'})
        assert r.status_code == 302
        assert '/login' in r.headers['Location']

    def test_ajouter_cree_tache_avec_bon_user(self, client):
        login_as_alice(client)
        client.post('/taches/ajouter', data={'titre': 'Nouvelle tâche'}, follow_redirects=True)
        with app.app_context():
            t = Tache.query.filter_by(titre='Nouvelle tâche').first()
            assert t is not None
            assert t.assignee == 'Alice'
            alice = User.query.filter_by(email='alice@test.com').first()
            assert t.user_id == alice.id

    def test_ajouter_redirige_vers_liste(self, client):
        login_as_alice(client)
        r = client.post('/taches/ajouter', data={'titre': 'Redirect test'})
        assert r.status_code == 302
        assert '/taches' in r.headers['Location']


# ── 3. COCHER ─────────────────────────────────────────────────────────────────

class TestCocherTache:
    def _get_tache_alice_id(self):
        with app.app_context():
            return Tache.query.filter_by(titre='Aspirateur').first().id

    def test_cocher_redirige_login_si_non_connecte(self, client):
        id_ = self._get_tache_alice_id()
        r = client.post(f'/taches/{id_}/cocher')
        assert r.status_code == 302
        assert '/login' in r.headers['Location']

    def test_cocher_sa_propre_tache(self, client):
        login_as_alice(client)
        id_ = self._get_tache_alice_id()
        client.post(f'/taches/{id_}/cocher', follow_redirects=True)
        with app.app_context():
            t = db.session.get(Tache, id_)
            assert t.faite is True

    def test_cocher_deux_fois_remet_a_false(self, client):
        login_as_alice(client)
        id_ = self._get_tache_alice_id()
        client.post(f'/taches/{id_}/cocher', follow_redirects=True)
        client.post(f'/taches/{id_}/cocher', follow_redirects=True)
        with app.app_context():
            t = db.session.get(Tache, id_)
            assert t.faite is False

    def test_cocher_tache_dautrui_refuse(self, client):
        """Bob ne peut pas cocher la tâche d'Alice."""
        login_as_bob(client)
        id_ = self._get_tache_alice_id()
        client.post(f'/taches/{id_}/cocher', follow_redirects=True)
        with app.app_context():
            t = db.session.get(Tache, id_)
            assert t.faite is False  # inchangé

    def test_cocher_tache_dautrui_flash_erreur(self, client):
        login_as_bob(client)
        id_ = self._get_tache_alice_id()
        r = client.post(f'/taches/{id_}/cocher', follow_redirects=True)
        assert "ne pouvez pas modifier" in r.data.decode()

    def test_cocher_tache_inexistante_retourne_404(self, client):
        login_as_alice(client)
        r = client.post('/taches/99999/cocher')
        assert r.status_code == 404

    def test_cocher_via_get_non_autorise(self, client):
        """La route cocher n'accepte que POST."""
        login_as_alice(client)
        id_ = self._get_tache_alice_id()
        r = client.get(f'/taches/{id_}/cocher')
        assert r.status_code == 405


# ── 4. SUPPRIMER ──────────────────────────────────────────────────────────────

class TestSupprimerTache:
    def _get_tache_alice_id(self):
        with app.app_context():
            return Tache.query.filter_by(titre='Aspirateur').first().id

    def test_supprimer_redirige_login_si_non_connecte(self, client):
        id_ = self._get_tache_alice_id()
        r = client.post(f'/taches/{id_}/supprimer')
        assert r.status_code == 302
        assert '/login' in r.headers['Location']

    def test_supprimer_sa_propre_tache(self, client):
        login_as_alice(client)
        id_ = self._get_tache_alice_id()
        client.post(f'/taches/{id_}/supprimer', follow_redirects=True)
        with app.app_context():
            assert db.session.get(Tache, id_) is None

    def test_supprimer_tache_dautrui_refuse(self, client):
        """Bob ne peut pas supprimer la tâche d'Alice."""
        login_as_bob(client)
        id_ = self._get_tache_alice_id()
        client.post(f'/taches/{id_}/supprimer', follow_redirects=True)
        with app.app_context():
            assert db.session.get(Tache, id_) is not None  # toujours là

    def test_supprimer_tache_dautrui_flash_erreur(self, client):
        login_as_bob(client)
        id_ = self._get_tache_alice_id()
        r = client.post(f'/taches/{id_}/supprimer', follow_redirects=True)
        assert "ne pouvez pas supprimer" in r.data.decode()

    def test_supprimer_tache_inexistante_retourne_404(self, client):
        login_as_alice(client)
        r = client.post('/taches/99999/supprimer')
        assert r.status_code == 404

    def test_supprimer_via_get_non_autorise(self, client):
        """La route supprimer n'accepte que POST."""
        login_as_alice(client)
        id_ = self._get_tache_alice_id()
        r = client.get(f'/taches/{id_}/supprimer')
        assert r.status_code == 405


# ── 5. TÂCHE LEGACY (sans propriétaire) ──────────────────────────────────────

class TestTacheLegacy:
    def _get_tache_legacy_id(self):
        with app.app_context():
            return Tache.query.filter_by(titre='Cuisine').first().id

    def test_legacy_visible_dans_la_liste(self, client):
        r = client.get('/taches')
        assert b'Cuisine' in r.data

    def test_legacy_non_cochable_par_alice(self, client):
        """Tâche sans user_id ne peut pas être cochée (user_id None != alice.id)."""
        login_as_alice(client)
        id_ = self._get_tache_legacy_id()
        client.post(f'/taches/{id_}/cocher', follow_redirects=True)
        with app.app_context():
            t = db.session.get(Tache, id_)
            assert t.faite is False

    def test_legacy_non_supprimable_par_alice(self, client):
        login_as_alice(client)
        id_ = self._get_tache_legacy_id()
        client.post(f'/taches/{id_}/supprimer', follow_redirects=True)
        with app.app_context():
            assert db.session.get(Tache, id_) is not None
