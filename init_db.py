import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('coloc.db')
c = conn.cursor()

# Création de la table users
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    prenom   TEXT NOT NULL,
    email    TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# 5 faux comptes de test
users = [
    ('Leo',   'leo@coloc.fr',   'leo1234'),
    ('Marie', 'marie@coloc.fr', 'marie5678'),
    ('Tom',   'tom@coloc.fr',   'tom0000'),
    ('Julie', 'julie@coloc.fr', 'julie99'),
    ('Alex',  'alex@coloc.fr',  'alex2025'),
]

for prenom, email, password in users:
    try:
        c.execute(
            'INSERT INTO users (prenom, email, password) VALUES (?, ?, ?)',
            (prenom, email, generate_password_hash(password))
        )
        print(f'✅ {email} créé')
    except sqlite3.IntegrityError:
        print(f'⚠️  {email} existe déjà, ignoré')

conn.commit()
conn.close()
print('\nBase de données coloc.db prête !')
