from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = 'coloc-voltaire-secret-2026'
CORS(app, supports_credentials=True)

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
FRONT_DIR = os.path.join(BASE_DIR, 'front')
DB        = os.path.join(BASE_DIR, 'coloc.db')

# ══════════════════════════════════════
# INIT BASE DE DONNÉES
# ══════════════════════════════════════
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Table users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            email    TEXT UNIQUE NOT NULL,
            pin_hash TEXT NOT NULL,
            color    TEXT NOT NULL,
            role     TEXT DEFAULT 'coloc',
            created  DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

    # Table depenses — avec categorie, statut, nb_parts
    c.execute('''
        CREATE TABLE IF NOT EXISTS depenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            montant     REAL NOT NULL,
            description TEXT,
            categorie   TEXT DEFAULT 'Autre',
            statut      TEXT DEFAULT 'pending',
            nb_parts    INTEGER DEFAULT 4,
            date        DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id     INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')

    # Table tasks — avec titre, statut, priorité, date due
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            titre       TEXT NOT NULL,
            description TEXT,
            statut      TEXT DEFAULT 'todo',
            priorite    TEXT DEFAULT 'normal',
            date_due    DATE,
            user_id     INTEGER,
            created     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')

    # Table reservations — planning des espaces communs
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        DATE NOT NULL,
            salle       TEXT NOT NULL,
            profil      TEXT NOT NULL,
            statut      TEXT DEFAULT 'Réservé',
            debut       TIME NOT NULL,
            fin         TIME NOT NULL,
            user_id     INTEGER,
            created     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')

    # Insertion des colocataires (ignoré si déjà existant)
    colocataires = [
        ('Eoghan',   'eoghan@coloc.fr',   '1111', '#5B6CFF', 'coloc'),
        ('François', 'francois@coloc.fr', '2222', '#FF7A59', 'admin'),
        ('Nassim',   'nassim@coloc.fr',   '3333', '#34D399', 'admin'),
    ]
    for name, email, pin, color, role in colocataires:
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        c.execute('''
            INSERT OR IGNORE INTO users (name, email, pin_hash, color, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, pin_hash, color, role))

    # Données de démo si la table depenses est vide


    conn.commit()
    conn.close()
    print('✅ Base de données initialisée')


# ══════════════════════════════════════
# ROUTES STATIQUES (sert le front)
# ══════════════════════════════════════
@app.route('/')
def index():
    return send_from_directory(FRONT_DIR, 'login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(FRONT_DIR, filename)


# ══════════════════════════════════════
# ROUTES API — USERS
# ══════════════════════════════════════

# GET /api/users — liste tous les users (sans pin_hash)
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db()
    users = conn.execute(
        'SELECT id, name, email, color, role FROM users ORDER BY id'
    ).fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

# GET /api/names — liste tous les noms d'utilisateurs
@app.route('/api/names', methods=['GET'])
def get_user_names():
    conn = get_db()
    names = [row['name'] for row in conn.execute('SELECT name FROM users').fetchall()]
    conn.close()
    return jsonify(names)


# ══════════════════════════════════════
# ROUTES API — DÉPENSES
# ══════════════════════════════════════

# GET /api/depenses — toutes les dépenses avec infos user
@app.route('/api/depenses', methods=['GET'])
def get_depenses():
    conn = get_db()
    rows = conn.execute('''
        SELECT d.id, d.montant, d.description, d.categorie, d.statut,
               d.nb_parts, d.date, u.name, u.color, u.id as user_id
        FROM depenses d
        LEFT JOIN users u ON d.user_id = u.id
        ORDER BY d.date DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# POST /api/depenses — ajouter une dépense
@app.route('/api/depenses', methods=['POST'])
def add_depense():
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    data = request.get_json()
    montant     = data.get('montant')
    description = data.get('description', '')
    categorie   = data.get('categorie', 'Autre')
    nb_parts    = data.get('nb_parts', 4)
    # user_id_override : permet de choisir qui a payé depuis la modale
    user_id = data.get('user_id_override', session['user_id'])

    if not montant:
        return jsonify({'error': 'Montant requis'}), 400

    conn = get_db()
    conn.execute('''
        INSERT INTO depenses (montant, description, categorie, nb_parts, user_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (montant, description, categorie, nb_parts, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201

# GET /api/soldes — calcule le solde net de chaque colocataire
@app.route('/api/soldes', methods=['GET'])
def get_soldes():
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    conn = get_db()
    users    = conn.execute('SELECT id, name, color FROM users ORDER BY id').fetchall()
    depenses = conn.execute('''
        SELECT montant, nb_parts, user_id FROM depenses WHERE statut != 'paid'
    ''').fetchall()
    conn.close()

    # Solde net par personne :
    # +X = les autres lui doivent de l'argent (il a avancé)
    # -X = il doit de l'argent aux autres
    soldes = {u['id']: {'name': u['name'], 'color': u['color'], 'solde': 0.0} for u in users}
    for dep in depenses:
        if dep['user_id'] is None:
            continue
        part = dep['montant'] / dep['nb_parts']
        for uid in soldes:
            if uid == dep['user_id']:
                soldes[uid]['solde'] += dep['montant'] - part  # récupère les parts des autres
            else:
                soldes[uid]['solde'] -= part                   # doit sa part

    return jsonify(list(soldes.values()))

# GET /api/remboursements — liste les remboursements suggérés (qui doit à qui)
@app.route('/api/remboursements', methods=['GET'])
def get_remboursements():
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    conn = get_db()
    users    = conn.execute('SELECT id, name, color FROM users ORDER BY id').fetchall()
    depenses = conn.execute('''
        SELECT montant, nb_parts, user_id FROM depenses WHERE statut != 'paid'
    ''').fetchall()
    conn.close()

    # Même calcul que /api/soldes
    soldes = {u['id']: {'id': u['id'], 'name': u['name'], 'color': u['color'], 'solde': 0.0} for u in users}
    for dep in depenses:
        if dep['user_id'] is None:
            continue
        part = dep['montant'] / dep['nb_parts']
        for uid in soldes:
            if uid == dep['user_id']:
                soldes[uid]['solde'] += dep['montant'] - part
            else:
                soldes[uid]['solde'] -= part

    # Algorithme de simplification des dettes
    debiteurs  = sorted([s for s in soldes.values() if s['solde'] < -0.01], key=lambda x: x['solde'])
    creanciers = sorted([s for s in soldes.values() if s['solde'] > 0.01],  key=lambda x: -x['solde'])

    remboursements = []
    i, j = 0, 0
    debiteurs  = [dict(d) for d in debiteurs]
    creanciers = [dict(c) for c in creanciers]

    while i < len(debiteurs) and j < len(creanciers):
        montant = min(-debiteurs[i]['solde'], creanciers[j]['solde'])
        if montant > 0.01:
            remboursements.append({
                'de':      debiteurs[i]['name'],
                'de_color': debiteurs[i]['color'],
                'a':       creanciers[j]['name'],
                'a_color':  creanciers[j]['color'],
                'montant': round(montant, 2),
            })
        debiteurs[i]['solde']  += montant
        creanciers[j]['solde'] -= montant
        if abs(debiteurs[i]['solde'])  < 0.01: i += 1
        if abs(creanciers[j]['solde']) < 0.01: j += 1

    return jsonify(remboursements)


# ══════════════════════════════════════
# ROUTES API — TÂCHES
# ══════════════════════════════════════

# GET /api/tasks — toutes les tâches
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db()
    rows = conn.execute('''
        SELECT t.id, t.titre, t.description, t.statut, t.priorite,
               t.date_due, t.user_id, u.name, u.color, t.created
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.id
        ORDER BY 
            CASE WHEN t.statut = 'todo' THEN 0 WHEN t.statut = 'in_progress' THEN 1 ELSE 2 END,
            t.date_due ASC,
            t.created DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# POST /api/tasks — créer une tâche
@app.route('/api/tasks', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    data = request.get_json()
    titre = data.get('titre', '').strip()
    description = data.get('description', '').strip()
    priorite = data.get('priorite', 'normal')
    date_due = data.get('date_due')
    user_id = session['user_id']
    
    if not titre:
        return jsonify({'error': 'Titre requis'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO tasks (titre, description, priorite, date_due, user_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (titre, description, priorite, date_due, user_id))
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'id': task_id}), 201

# PUT /api/tasks/<id> — modifier une tâche
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    data = request.get_json()
    statut = data.get('statut')
    priorite = data.get('priorite')
    titre = data.get('titre')
    description = data.get('description')
    
    conn = get_db()
    updates = []
    values = []
    
    if statut is not None:
        updates.append('statut = ?')
        values.append(statut)
    if priorite is not None:
        updates.append('priorite = ?')
        values.append(priorite)
    if titre is not None:
        updates.append('titre = ?')
        values.append(titre)
    if description is not None:
        updates.append('description = ?')
        values.append(description)
    
    if not updates:
        conn.close()
        return jsonify({'error': 'Aucune modification'}), 400
    
    values.append(task_id)
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    conn.execute(query, values)
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# DELETE /api/tasks/<id> — supprimer une tâche
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    conn = get_db()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


# ══════════════════════════════════════
# ROUTES API — RÉSERVATIONS
# ══════════════════════════════════════

# GET /api/reservations — toutes les réservations
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    conn = get_db()
    rows = conn.execute('''
        SELECT r.id, r.date, r.salle, r.profil, r.statut,
               r.debut, r.fin, r.user_id, u.name, u.color, r.created
        FROM reservations r
        LEFT JOIN users u ON r.user_id = u.id
        ORDER BY r.date DESC, r.debut ASC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# POST /api/reservations — créer une réservation
@app.route('/api/reservations', methods=['POST'])
def add_reservation():
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    data = request.get_json()
    date = data.get('date')
    salle = data.get('salle', '').strip()
    profil = data.get('profil', '').strip()
    statut = data.get('statut', 'Réservé')
    debut = data.get('debut')
    fin = data.get('fin')
    user_id = session['user_id']
    
    if not all([date, salle, profil, debut, fin]):
        return jsonify({'error': 'Tous les champs sont requis'}), 400
    
    if fin <= debut:
        return jsonify({'error': 'Heure de fin doit être après l\'heure de début'}), 400
    
    # Vérifier les conflits
    conn = get_db()
    conflict = conn.execute('''
        SELECT id FROM reservations
        WHERE salle = ? AND date = ? AND debut < ? AND fin > ?
    ''', (salle, date, fin, debut)).fetchone()
    
    if conflict:
        conn.close()
        return jsonify({'error': 'Conflit avec une réservation existante'}), 409
    
    c = conn.cursor()
    c.execute('''
        INSERT INTO reservations (date, salle, profil, statut, debut, fin, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date, salle, profil, statut, debut, fin, user_id))
    conn.commit()
    res_id = c.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'id': res_id}), 201

# PUT /api/reservations/<id> — modifier une réservation
@app.route('/api/reservations/<int:res_id>', methods=['PUT'])
def update_reservation(res_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    data = request.get_json()
    date = data.get('date')
    salle = data.get('salle')
    profil = data.get('profil')
    statut = data.get('statut')
    debut = data.get('debut')
    fin = data.get('fin')
    
    conn = get_db()
    updates = []
    values = []
    
    if date:
        updates.append('date = ?')
        values.append(date)
    if salle:
        updates.append('salle = ?')
        values.append(salle)
    if profil:
        updates.append('profil = ?')
        values.append(profil)
    if statut:
        updates.append('statut = ?')
        values.append(statut)
    if debut:
        updates.append('debut = ?')
        values.append(debut)
    if fin:
        updates.append('fin = ?')
        values.append(fin)
    
    if not updates:
        conn.close()
        return jsonify({'error': 'Aucune modification'}), 400
    
    # Vérifier les conflits (en excluant la résa qu'on modifie)
    if date and salle and debut and fin:
        conflict = conn.execute('''
            SELECT id FROM reservations
            WHERE id != ? AND salle = ? AND date = ? AND debut < ? AND fin > ?
        ''', (res_id, salle, date, fin, debut)).fetchone()
        
        if conflict:
            conn.close()
            return jsonify({'error': 'Conflit avec une réservation existante'}), 409
    
    values.append(res_id)
    query = f"UPDATE reservations SET {', '.join(updates)} WHERE id = ?"
    conn.execute(query, values)
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# DELETE /api/reservations/<id> — supprimer une réservation
@app.route('/api/reservations/<int:res_id>', methods=['DELETE'])
def delete_reservation(res_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    
    conn = get_db()
    conn.execute('DELETE FROM reservations WHERE id = ?', (res_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


# ══════════════════════════════════════
# ROUTES API — AUTH
# ══════════════════════════════════════

# POST /api/login — vérifie le PIN et ouvre la session
@app.route('/api/login', methods=['POST'])
def login():
    data  = request.get_json()
    email = data.get('email', '').strip().lower()
    pin   = data.get('pin', '').strip()

    if not email or not pin:
        return jsonify({'error': 'Email et PIN requis'}), 400

    pin_hash = hashlib.sha256(pin.encode()).hexdigest()

    conn = get_db()
    user = conn.execute(
        'SELECT id, name, email, color, role FROM users WHERE email=? AND pin_hash=?',
        (email, pin_hash)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({'error': 'PIN incorrect'}), 401

    session['user_id']    = user['id']
    session['user_name']  = user['name']
    session['user_email'] = user['email']
    session['user_role']  = user['role']
    session['user_color'] = user['color']

    return jsonify({'success': True, 'user': dict(user)})

# POST /api/logout — ferme la session
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

# GET /api/me — retourne le user connecté (avec color)
@app.route('/api/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    conn = get_db()
    user = conn.execute(
        'SELECT id, name, email, color, role FROM users WHERE id=?',
        (session['user_id'],)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({'error': 'Utilisateur introuvable'}), 404

    return jsonify(dict(user))


# ══════════════════════════════════════
# LANCEMENT
# ══════════════════════════════════════
if __name__ == '__main__':
    init_db()
    print('🏡 CoLoc API lancée sur http://127.0.0.1:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)