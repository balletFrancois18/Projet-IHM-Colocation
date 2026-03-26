# 🏠 Colocation Manager - Application IHM

Une application web complète de **gestion de colocation** développée avec **Flask** (backend) et **Vanilla JavaScript** (frontend). Parfaite pour tablette grâce à son interface responsive.

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Stack Technique](#-stack-technique)
- [Installation](#-installation)
- [Lancement](#-lancement)
- [Architecture](#-architecture)
- [Utilisation](#-utilisation)
- [API Endpoints](#-api-endpoints)

---

## ✨ Fonctionnalités

### 🎯 Dashboard
- **Dépenses récentes** - Visualisation instantanée des derniers paiements
- **Tâches du jour** - Tâches prioritaires à accomplir
- **Calendrier de la semaine** - Vue des événements programmés
- **Activité récente** - Flux d'activités avec timestamps précis
- **Réservations de la semaine** - Consultation des réservations de salles

### 💸 Gestion des Dépenses
- Ajouter/modifier/supprimer des dépenses
- Catégorisation automatique (Courses, Factures, Sorties, etc.)
- Suivi des soldes entre colocataires
- Suggestions de remboursement intelligentes

### 🧹 Gestion des Tâches
- Vue Kanban (À faire → En cours → Fait)
- Assignation de tâches par personne
- Mise à jour en temps réel du dashboard
- Filtrage par statut

### 📅 Réservation de Salles
- Calendrier interactif par pièce (Cuisine, Salon, Salle de bain, etc.)
- Statuts: Réservé, Occupé, Disponible
- Visualisation de la semaine complète

### 💬 Chat Intégré
- Messagerie en temps réel
- Liste des membres en ligne
- Messages épinglés

### 🔐 Authentification
- Connexion par PIN (sécurisée)
- Session persistante via localStorage
- Déconnexion avec confirmation

---

## 🛠️ Stack Technique

| Couche | Technologie |
|--------|------------|
| **Backend** | Flask 2.x + SQLite3 |
| **Frontend** | Vanilla JavaScript (ES6+) |
| **Styling** | CSS3 (Variables CSS, Grid, Flexbox) |
| **Base de Données** | SQLite3 (4 tables normalisées) |
| **API** | RESTful JSON + CORS |
| **Authentification** | Session-based |

---

## 🚀 Installation

### Prérequis
- **Python 3.8+**
- **pip** (gestionnaire de paquets Python)

### Étapes

1. **Cloner/accéder au projet**
```bash
cd "c:\Users\ELEVES\Documents\LP3\Coloc\Projet-IHM-Colocation"
```

2. **Créer un environnement virtuel** (optionnel mais recommandé)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install flask flask-cors
```

4. **Vérifier l'installation**
```bash
pip list
# Doit afficher: Flask, Flask-Cors
```

---

## 🎮 Lancement

### Démarrer le serveur

```bash
cd "c:\Users\ELEVES\Documents\LP3\Coloc\Projet-IHM-Colocation"
python app.py
```

**Sortie attendue:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Accéder à l'application

Ouvrez votre navigateur et allez à: **http://localhost:5000/login.html**

### Identifiants par défaut

| Utilisateur | PIN | Rôle |
|------------|-----|------|
| Alice | 1234 | Admin |
| Bob | 5678 | Coloc |
| Charlie | 9012 | Coloc |
| Diana | 3456 | Coloc |

---

## 🏗️ Architecture

### Structure des fichiers
```
Projet-IHM-Colocation/
├── app.py                 # Backend Flask
├── coloc.db              # Base de données SQLite
├── front/
│   ├── index.html        # Dashboard principal (1889 lignes)
│   ├── login.html        # Page de connexion
│   ├── style.css         # Styles globaux (860 lignes)
│   └── style-login.css   # Styles login (248 lignes)
└── README.md             # Cette documentation
```

### Schéma de la base de données

```sql
users          depenses       tasks         reservations
├─ id          ├─ id          ├─ id         ├─ id
├─ name        ├─ montant     ├─ titre      ├─ salle
├─ email       ├─ description ├─ statut     ├─ debut
├─ pin_hash    ├─ categorie   ├─ user_id    ├─ fin
├─ color       ├─ statut      ├─ date       ├─ date
└─ role        ├─ nb_parts    └─ created    ├─ user_id
               ├─ date        └─ updated    └─ statut
               ├─ user_id
               └─ created
```

### Workflow de rendu

```
Page charger
    ↓
Fetch données API (tasks, depenses, reservations)
    ↓
Stocker dans localStorage
    ↓
Appeler fonctions render* (renderDashboard, renderActivityFeed, etc.)
    ↓
Afficher widgets
    ↓
Écouter changements (onclick, form submit)
    ↓
Appeler reloadDashboard() pour mise à jour temps réel
```

---

## 💻 Utilisation

### Navigation principale

| Écran | Accès | Fonction |
|-------|-------|----------|
| 🏠 **Dashboard** | Accueil | Vue d'ensemble synthétique |
| 💸 **Dépenses** | Menu | Gestion complète des dépenses |
| 🧹 **Tâches** | Menu | Kanban des tâches |
| 📅 **Réservations** | Menu ou widget | Calendrier des salles |
| 💬 **Chat** | Menu | Messagerie d'équipe |

### Actions clés

**Ajouter une dépense:**
- Cliquer sur "＋ Nouvelle dépense"
- Remplir le formulaire (montant, description, catégorie)
- Valider

**Changer le statut d'une tâche:**
- Cliquer sur une tâche dans le Kanban
- Glisser-déposer ou cliquer sur le statut
- Dashboard se met à jour automatiquement

**Réserver une salle:**
- Aller dans Réservations
- Cliquer sur une case dans le calendrier
- Entrer l'horaire et confirmer

**Se déconnecter:**
- Cliquer sur le bloc profil (bas de la sidebar)
- Confirmer dans le popup

---

## 🔌 API Endpoints

### Authentification
```
POST   /api/login              # Connexion
POST   /api/logout             # Déconnexion
GET    /api/me                 # Profil utilisateur actuel
GET    /api/users              # Liste de tous les utilisateurs
```

### Dépenses
```
GET    /api/depenses           # Toutes les dépenses
POST   /api/depenses           # Créer une dépense
PUT    /api/depenses/<id>      # Modifier une dépense
DELETE /api/depenses/<id>      # Supprimer une dépense
GET    /api/soldes             # Soldes entre colocataires
GET    /api/remboursements     # Suggestions de remboursement
```

### Tâches
```
GET    /api/tasks              # Toutes les tâches
POST   /api/tasks              # Créer une tâche
PUT    /api/tasks/<id>         # Modifier une tâche
DELETE /api/tasks/<id>         # Supprimer une tâche
```

### Réservations
```
GET    /api/reservations       # Toutes les réservations
POST   /api/reservations       # Créer une réservation
PUT    /api/reservations/<id>  # Modifier une réservation
DELETE /api/reservations/<id>  # Supprimer une réservation
```

---

## 🎨 Design System

### Couleurs
- **Primary**: `#5B6CFF` - Actions principales (bleu)
- **Accent**: `#FF7A59` - Actions secondaires (orange)
- **Success**: `#34D399` - Validations (vert)
- **Background**: `#F6F8FC` - Fond principal
- **Text Dark**: `#1F2937` - Texte principal
- **Text Muted**: `#9CA3AF` - Texte secondaire

### Typographie
- **Font**: DM Sans, Syne (headings)
- **Sizes**: 13px (small), 14px (body), 16px (title), 22px (heading)
- **Weights**: 400, 500, 600, 700

---

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier que Flask est installé
pip install flask flask-cors

# Vérifier le port 5000 n'est pas occupé
netstat -ano | findstr :5000
```

### Les widgets ne se mettent pas à jour
- Rafraîchir la page (F5)
- Vérifier la console (F12 > Console) pour les erreurs
- Vérifier que le backend tourne: `http://localhost:5000/api/tasks`

### Base de données corrompue
- Arrêter le serveur
- Supprimer `coloc.db`
- Relancer le serveur (elle se recréera avec les données demo)

---

## 📱 Responsive Design

L'application est optimisée pour:
- ✅ **Tablettes** (768px - 1024px) - Recommandé
- ✅ **Desktop** (1024px+)
- ✅ **Mobile** (320px - 767px) - Support basique

---

## 👥 Auteurs & Crédits

**Développement:** Projet IHM - LP3 Voltaire
**Technologies:** Flask, Vanilla JS, SQLite
**Date:** Mars 2026

---

## 📄 License

Projet à usage interne.

---

## 📞 Support

Pour toute question ou bug:
1. Consultant la documentation technique
2. Vérifier les logs du serveur (terminal)
3. Vérifier la console du navigateur (F12)
4. Consulter les fichiers source commentés

---

**Bonne gestion! 🎉**
