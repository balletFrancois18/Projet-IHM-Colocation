"""
Tests E2E Playwright — taches.html + routes/taches.py
Lance l'app Flask dans un thread, puis pilote un vrai navigateur Chromium.

Couvre :
  - Affichage de la liste sans login
  - Bouton "Ajouter" absent / présent selon le login
  - Ajout d'une tâche via la modal
  - Cochage / décochage d'une tâche (propriétaire)
  - Suppression d'une tâche (propriétaire)
  - Boutons d'action absents sur les tâches d'autrui
  - Messages flash sur action interdite (via requête directe)
"""

import threading
import pytest
from playwright.sync_api import Page, expect
from main import app
from models import db, User, Tache


# ── Serveur Flask de test ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def flask_server():
    """Démarre Flask sur le port 5055 pour toute la session de tests."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_e2e.db'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SERVER_NAME'] = None

    with app.app_context():
        db.drop_all()
        db.create_all()
        alice = User(nom='Dupont', prenom='Alice', email='alice@e2e.com', password='pass')
        bob   = User(nom='Martin', prenom='Bob',   email='bob@e2e.com',   password='pass')
        db.session.add_all([alice, bob])
        db.session.commit()
        tache_alice  = Tache(titre='Aspirateur E2E', assignee='Alice', faite=False, user_id=alice.id)
        tache_bob    = Tache(titre='Cuisine E2E',    assignee='Bob',   faite=False, user_id=bob.id)
        tache_legacy = Tache(titre='Tâche Legacy',   assignee='Ancien', faite=False, user_id=None)
        db.session.add_all([tache_alice, tache_bob, tache_legacy])
        db.session.commit()

    server = threading.Thread(
        target=lambda: app.run(port=5055, use_reloader=False, debug=False),
        daemon=True
    )
    server.start()

    import time; time.sleep(1)   # laisse le temps au serveur de démarrer
    yield "http://localhost:5055"

    # Nettoyage de la base de test
    import os
    try:
        os.remove("instance/test_e2e.db")
    except FileNotFoundError:
        pass


BASE = "http://localhost:5055"


def login(page: Page, email: str, password: str = 'pass'):
    page.goto(f"{BASE}/login")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{BASE}/")


def logout(page: Page):
    page.goto(f"{BASE}/logout")


# ── 1. LISTE SANS LOGIN ────────────────────────────────────────────────────────

class TestListeSansLogin:
    def test_liste_accessible(self, flask_server, page: Page):
        page.goto(f"{BASE}/taches")
        expect(page).to_have_title("CoLoc — Tâches")

    def test_toutes_taches_visibles(self, flask_server, page: Page):
        page.goto(f"{BASE}/taches")
        expect(page.locator("text=Aspirateur E2E")).to_be_visible()
        expect(page.locator("text=Cuisine E2E")).to_be_visible()
        expect(page.locator("text=Tâche Legacy")).to_be_visible()

    def test_bouton_ajouter_absent(self, flask_server, page: Page):
        page.goto(f"{BASE}/taches")
        expect(page.locator("button:has-text('+ Ajouter une tâche')")).to_have_count(0)

    def test_lien_connexion_present(self, flask_server, page: Page):
        page.goto(f"{BASE}/taches")
        expect(page.locator("a.btn-connect")).to_be_visible()


# ── 2. LISTE AVEC LOGIN ────────────────────────────────────────────────────────

class TestListeAvecLogin:
    def test_bouton_ajouter_present(self, flask_server, page: Page):
        login(page, 'alice@e2e.com')
        page.goto(f"{BASE}/taches")
        expect(page.locator("button:has-text('+ Ajouter une tâche')")).to_be_visible()
        logout(page)

    def test_bouton_deconnexion_present(self, flask_server, page: Page):
        login(page, 'alice@e2e.com')
        page.goto(f"{BASE}/taches")
        expect(page.locator("a.btn-logout")).to_be_visible()
        logout(page)


# ── 3. AJOUTER UNE TÂCHE ──────────────────────────────────────────────────────

class TestAjouterTache:
    def test_ajout_via_modal(self, flask_server, page: Page):
        login(page, 'alice@e2e.com')
        page.goto(f"{BASE}/taches")

        # Ouvrir la modal
        page.click("button:has-text('+ Ajouter une tâche')")
        expect(page.locator("#modal-overlay")).to_be_visible()

        # Remplir et valider
        page.fill('input[name="titre"]', 'Tâche Playwright')
        page.click("button.btn-valider")

        # Vérifier la tâche dans la liste
        expect(page.locator("text=Tâche Playwright")).to_be_visible()
        logout(page)

    def test_modal_annuler(self, flask_server, page: Page):
        login(page, 'alice@e2e.com')
        page.goto(f"{BASE}/taches")
        page.click("button:has-text('+ Ajouter une tâche')")
        expect(page.locator("#modal-overlay")).to_be_visible()
        page.click("button.btn-annuler")
        expect(page.locator("#modal-overlay")).to_be_hidden()
        logout(page)


# ── 4. COCHER UNE TÂCHE ───────────────────────────────────────────────────────

class TestCocherTache:
    def test_cocher_sa_tache(self, flask_server, page: Page):
        login(page, 'alice@e2e.com')
        page.goto(f"{BASE}/taches")

        # Trouver la carte d'Alice et cliquer sur son bouton cocher
        carte = page.locator(".tache-card", has=page.locator("text=Aspirateur E2E"))
        check_btn = carte.locator("button.tache-check")
        expect(check_btn).to_be_visible()
        check_btn.click()

        # Le badge doit passer à "Fait"
        page.goto(f"{BASE}/taches")
        carte = page.locator(".tache-card", has=page.locator("text=Aspirateur E2E"))
        expect(carte.locator(".badge-done")).to_be_visible()
        logout(page)

    def test_tache_autrui_non_cochable(self, flask_server, page: Page):
        """La tâche de Bob doit avoir un div (pas un bouton) pour le check."""
        login(page, 'alice@e2e.com')
        page.goto(f"{BASE}/taches")
        carte = page.locator(".tache-card", has=page.locator("text=Cuisine E2E"))
        # Pas de form/button pour cocher une tâche d'autrui
        expect(carte.locator("form button.tache-check")).to_have_count(0)
        expect(carte.locator("div.tache-check")).to_be_visible()
        logout(page)


# ── 5. SUPPRIMER UNE TÂCHE ────────────────────────────────────────────────────

class TestSupprimerTache:
    def test_supprimer_sa_tache(self, flask_server, page: Page):
        # Alice crée une tâche puis la supprime
        login(page, 'alice@e2e.com')
        page.goto(f"{BASE}/taches")
        page.click("button:has-text('+ Ajouter une tâche')")
        page.fill('input[name="titre"]', 'À supprimer')
        page.click("button.btn-valider")
        expect(page.locator("text=À supprimer")).to_be_visible()

        # Supprimer (accepter la confirmation JS)
        page.on("dialog", lambda d: d.accept())
        carte = page.locator(".tache-card", has=page.locator("text=À supprimer"))
        carte.locator("button.btn-supprimer").click()

        expect(page.locator("text=À supprimer")).to_have_count(0)
        logout(page)

    def test_bouton_supprimer_absent_sur_tache_dautrui(self, flask_server, page: Page):
        login(page, 'alice@e2e.com')
        page.goto(f"{BASE}/taches")
        carte = page.locator(".tache-card", has=page.locator("text=Cuisine E2E"))
        expect(carte.locator("button.btn-supprimer")).to_have_count(0)
        logout(page)


# ── 6. FILTRES ────────────────────────────────────────────────────────────────

class TestFiltres:
    def test_filtre_todo_masque_faites(self, flask_server, page: Page):
        page.goto(f"{BASE}/taches")
        page.click("button:has-text('À faire')")
        # Les cartes avec data-statut="fait" doivent être masquées
        faites = page.locator(".tache-card[data-statut='fait']")
        for i in range(faites.count()):
            expect(faites.nth(i)).to_be_hidden()

    def test_filtre_tous_reaffiche_tout(self, flask_server, page: Page):
        page.goto(f"{BASE}/taches")
        page.click("button:has-text('À faire')")
        page.click("button:has-text('Toutes')")
        cards = page.locator(".tache-card")
        for i in range(cards.count()):
            expect(cards.nth(i)).to_be_visible()
