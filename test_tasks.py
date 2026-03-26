import requests

# Login
sess = requests.Session()
r = sess.post('http://127.0.0.1:5000/api/login', json={'email':'eoghan@coloc.fr','pin':'1111'})
print('Login:', r.json()['success'])

# Create task
r = sess.post('http://127.0.0.1:5000/api/tasks', json={
    'titre': 'Nettoyer salle de bain',
    'description': 'Zone principale',
    'priorite': 'haute',
    'date_due': '2026-03-27'
})
print('Create Status:', r.status_code)
print('Create Response text:', r.text)
if r.status_code == 201 or r.status_code == 200:
    print('Create Response:', r.json())

# Get tasks
r2 = sess.get('http://127.0.0.1:5000/api/tasks')
tasks = r2.json()
print(f'Tasks count: {len(tasks)}')
for i, t in enumerate(tasks[:3]):  # Show first 3
    print(f'  {i+1}. {t["titre"]} (statut: {t["statut"]}, priorite: {t["priorite"]})')

