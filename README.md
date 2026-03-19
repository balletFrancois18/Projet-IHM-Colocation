# Projet-IHM-Colocation
Repos destiné aux travaux de groupes lié au Projet Collocation

Lien de la schematisation du projet : https://excalidraw.com/#room=5efa464f2d8a11ad5eb2,8UC290wY-AdvZbpdzNEJew




## plan


Projet-IHM-Colocation/
├── main.py              ✅ fait
├── models.py            ✅ fait
├── requirements.txt     ✅ fait
├── Procfile             ✅ fait
├── .gitignore           ✅ fait
├── routes/
│   ├── __init__.py      ✅ fait
│   ├── taches.py        ✅ fait
│   ├── depenses.py      ✅ fait
│   └── auth.py          ✅ fait
├── templates/
│   ├── index.html       ✅ fait
│   ├── login.html       ❌ à créer
│   ├── tache.html       ❌ à créer
│   └── ajouter_depense.html ✅ fait
├── static/
│   └── style.css        ✅ fait
└── coloc.db             ✅ auto-généré



# installations


Vérifie les packages Flask et Flask-SQLAlchemy installés sont dans la liste

```
pip list
```

## Mise en place de l'environnement

activer le venv à chaque nouveau terminal

```
source venv/bin/activate
```

Lancer Flask
```
python3 main.py
```


Pour éviter de l'oublier, tu peux ajouter ça dans ton .bashrc :
bashecho "alias coloc='cd ~/Downloads/Projet-IHM-Colocation-main2 && source venv/bin/activate'" >> ~/.bashrc

# 1er test relance Flask 
python3 main.py


source ~/.bashrc



# Sources 

https://css-irl.info/

https://www.geeksforgeeks.org/javascript/task-scheduler-using-html-css-and-js/




