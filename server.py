from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import check_password_hash
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'coloc.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Sert les fichiers statiques (HTML/CSS/JS) ──────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)


# ── API Login ──────────────────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email    = (data.get('email', '') or '').strip().lower()
    password = data.get('password', '') or ''

    if not email or not password:
        return jsonify({'error': 'Champs manquants'}), 400

    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE LOWER(email) = ?', (email,)
    ).fetchone()
    conn.close()

    if user is None or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

    return jsonify({'success': True, 'prenom': user['prenom']})


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print('⚠️  Base de données introuvable — lance d\'abord : python init_db.py')
    else:
        print('✅ Base de données trouvée')
    print('🚀 Serveur démarré sur http://localhost:5000')
    app.run(port=5000, debug=True)
