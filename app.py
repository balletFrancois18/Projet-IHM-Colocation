from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import os

app = Flask(__name__, static_folder='front')
app.secret_key = 'coloc-voltaire-secret-2026'  # change si tu veux
CORS(app, supports_credentials=True)

DB = 'coloc.db'

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
        )
    ''')

    # Insertion des colocataires (ignoré si déjà existant)
    colocataires = [
        ('Eoghan',  'eoghan@coloc.fr',  '1111', '#5B6CFF', 'coloc'),
        ('François','francois@coloc.fr', '2222', '#FF7A59', 'coloc'),
        ('Nassim',  'nassim@coloc.fr',  '3333', '#34D399', 'admin'),
        ('Loucia',  'loucia@coloc.fr',  '4444', '#F472B6', 'coloc'),
        ('Banu',    'banu@coloc.fr',    '5555', '#FBBF24', 'coloc'),
    ]

    for name, email, pin, color, role in colocataires:
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        c.execute('''
            INSERT OR IGNORE INTO users (name, email, pin_hash, color, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, pin_hash, color, role))

    conn.commit()
    conn.close()
    print('✅ Base de données initialisée')

# ══════════════════════════════════════
# ROUTES STATIQUES (sert le front)
# ══════════════════════════════════════
@app.route('/')
def index():
    return send_from_directory('front', 'login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('front', filename)

# ══════════════════════════════════════
# ROUTES API — USERS
# ══════════════════════════════════════

# GET /api/users — liste tous les users (sans pin_hash)
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db()
    users = conn.execute(
        'SELECT id, name, email, color, role FROM users ORDER BY name'
    ).fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

# POST /api/login — vérifie le PIN et ouvre la session
@app.route('/api/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = data.get('email', '').strip().lower()
    pin      = data.get('pin', '').strip()

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

    # Ouvre la session Flask
    session['user_id']    = user['id']
    session['user_name']  = user['name']
    session['user_email'] = user['email']
    session['user_role']  = user['role']

    return jsonify({
        'success': True,
        'user': dict(user)
    })

# POST /api/logout — ferme la session
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

# GET /api/me — retourne le user connecté
@app.route('/api/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401
    return jsonify({
        'id':    session['user_id'],
        'name':  session['user_name'],
        'email': session['user_email'],
        'role':  session['user_role'],
    })

# ══════════════════════════════════════
# LANCEMENT
# ══════════════════════════════════════
if __name__ == '__main__':
    init_db()
    print('🏡 CoLoc API lancée sur http://163.173.113.178:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)