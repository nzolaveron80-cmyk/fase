# Déploiement sur PythonAnywhere

Ce guide suppose un compte gratuit « Beginner » et un identifiant appelé **VOTREPSEUDO**
(à remplacer partout dans les commandes et fichiers).

---

## Étape 0 — Préparer le projet en local

1. Générer la première migration (obligatoire, elle doit être livrée avec le code) :
   ```bash
   python manage.py makemigrations core
   python manage.py migrate
   ```
   Le dossier `core/migrations/` doit contenir un fichier `0001_initial.py`.
2. Tester en mode développement :
   ```bash
   DJANGO_DEBUG=1 python manage.py runserver
   ```
3. Vérifier que le fichier `media/site/logo-upc.svg` existe.
4. Ne jamais livrer `.env`, `db.sqlite3`, `media/` ni `backups/` dans le code (ils sont dans `.gitignore`).

## Étape 1 — Mettre le code sur PythonAnywhere

Option recommandée : Git.
1. Poussez le projet sur GitHub (privé de préférence).
2. Dans la **console Bash** de PythonAnywhere :
   ```bash
   git clone https://github.com/VOTRE-COMPTE/fase-django.git ~/fase-django
   ```

Option simple : onglet **Files**, envoyez le zip, puis décompressez-le dans la console :
```bash
cd ~ && unzip fase-django.zip
```

## Étape 2 — Environnement virtuel

Dans la console Bash :
```bash
mkvirtualenv --python=/usr/bin/python3.12 fase
pip install -r ~/fase-django/requirements.txt
```
(Le nom `fase` doit correspondre au chemin `~/.virtualenvs/fase` utilisé par `deploy.sh`.)

## Étape 3 — Fichier `.env`

Générez une clé secrète :
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Créez le fichier de configuration :
```bash
cd ~/fase-django
cp .env.example .env
nano .env
```
Renseignez `DJANGO_SECRET_KEY` avec la clé générée et remplacez `VOTREPSEUDO` par votre identifiant.

## Étape 4 — Base de données, statiques et compte administrateur

```bash
cd ~/fase-django
source ~/.virtualenvs/fase/bin/activate
mkdir -p media
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Puis envoyez le logo via l'onglet **Files** dans `~/fase-django/media/site/logo-upc.svg`
(créez le dossier `site` s'il n'existe pas).
Les photos et documents envoyés depuis l'administration iront aussi dans `media/`.

## Étape 5 — Créer l'application web

Onglet **Web** > **Add a new web app** :
1. Choisir **Manual configuration** (pas l'assistant Django) et **Python 3.12**.
2. Dans la section **Code** :
   - *Source code* : `/home/VOTREPSEUDO/fase-django`
   - *Working directory* : `/home/VOTREPSEUDO/`
3. **Virtualenv** : `/home/VOTREPSEUDO/.virtualenvs/fase`
4. **WSGI configuration file** : ouvrez-le, supprimez tout le contenu et collez celui de
   `deploy/pythonanywhere_wsgi.py` (en remplaçant `VOTREPSEUDO`).
5. **Static files** — ajoutez deux entrées :
   | URL | Directory |
   |---|---|
   | `/static/` | `/home/VOTREPSEUDO/fase-django/staticfiles/` |
   | `/media/` | `/home/VOTREPSEUDO/fase-django/media/` |
6. Cliquez sur **Reload**.

Le site est accessible à `https://VOTREPSEUDO.pythonanywhere.com`.

## Étape 6 — Vérifications

- [ ] La page d'accueil s'affiche avec le logo.
- [ ] Les styles CSS sont appliqués (sinon, vérifier la correspondance `/static/`).
- [ ] `https://VOTREPSEUDO.pythonanywhere.com/admin/` permet de se connecter.
- [ ] Une actualité avec image s'affiche correctement (sinon, vérifier `/media/`).
- [ ] Le lien `http://` redirige vers `https://`.
- [ ] Les erreurs éventuelles sont dans l'onglet **Web** > **Error log**.

Contrôle de sécurité dans la console :
```bash
cd ~/fase-django && source ~/.virtualenvs/fase/bin/activate
python manage.py check --deploy
```

## Étape 7 — Mises à jour

Après chaque modification du code :
```bash
cd ~/fase-django
git pull            # ou : remplacer les fichiers via Files
bash deploy/deploy.sh
```
Puis **Reload** dans l'onglet Web.

## Étape 8 — Sauvegardes

Sauvegarde manuelle de la base :
```bash
cd ~/fase-django && source ~/.virtualenvs/fase/bin/activate
python manage.py backup_db --keep 14
```
Les copies sont dans `~/fase-django/backups/`. Pour une tâche automatique, onglet **Tasks**,
ajoutez une tâche quotidienne :
```
cd ~/fase-django && ~/.virtualenvs/fase/bin/python manage.py backup_db --keep 14
```
Les fichiers médias (`media/`) se sauvegardent à part, par exemple en les téléchargeant depuis l'onglet **Files**
ou avec `tar -czf ~/medias.tar.gz ~/fase-django/media`.

Téléchargez régulièrement les sauvegardes sur votre ordinateur : elles restent sur le même compte PythonAnywhere.

## Limites de l'offre gratuite à garder en tête

- Une seule application web, sous `VOTREPSEUDO.pythonanywhere.com` (pas de domaine personnalisé).
- Espace disque limité ; surveillez la taille de `media/` (onglet **Files**).
- L'application « s'endort » si elle n'est pas utilisée pendant un certain temps : la première visite peut être lente.
- Une seule tâche planifiée est généralement autorisée. Vérifiez les quotas actuels sur le site de PythonAnywhere.

## Dépannage rapide

| Symptôme | Cause probable |
|---|---|
| Page blanche / erreur 500 | Lire l'**Error log** ; vérifier `.env` et le chemin du virtualenv |
| Pas de style | Mapping `/static/` absent, ou `collectstatic` non lancé |
| Images cassées | Mapping `/media/` absent, ou fichier non envoyé dans `media/` |
| Erreur CSRF à la connexion admin | `DJANGO_CSRF_TRUSTED_ORIGINS` mal renseigné (doit commencer par `https://`) |
| Boucle de redirection HTTPS | Mettre `DJANGO_SECURE_SSL_REDIRECT=0` dans `.env`, puis Reload |
| `DJANGO_SECRET_KEY doit être défini` | Fichier `.env` absent ou incomplet |
