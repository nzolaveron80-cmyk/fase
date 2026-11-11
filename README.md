# Site FASE · UPC (Django + SQLite)

## Installation locale

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations core   # première fois uniquement
python manage.py migrate
python manage.py createsuperuser
DJANGO_DEBUG=1 python manage.py runserver
```

- Site : http://127.0.0.1:8000
- Administration : http://127.0.0.1:8000/admin

Sur Windows, définissez la variable avec `set DJANGO_DEBUG=1` avant `runserver`.

## Structure

- `core/` : modèles, vues, administration, commande `backup_db`
- `templates/` : pages HTML
- `static/` : CSS, JavaScript, logo (`static/img/logo-upc.svg`)
- `media/` : fichiers envoyés depuis l'administration (non versionnés)
- `deploy/` : script de mise à jour et configuration WSGI
- `DEPLOIEMENT.md` : guide de mise en ligne

## Avant chaque mise en ligne

1. `python manage.py makemigrations core` (si les modèles ont changé) et commit de `core/migrations/`.
2. Vérifier que `static/img/logo-upc.svg` est présent.
3. Vérifier qu'aucun secret n'est dans le code (`.env` reste local).
4. `python manage.py check --deploy`.

## Sauvegarde

```bash
python manage.py backup_db --keep 14
```
Variable optionnelle `DJANGO_BACKUP_DIR` pour choisir le dossier de sauvegarde.

## Attention : nom de l'environnement virtuel

N'appelez pas l'environnement virtuel `.env` : ce nom est réservé au fichier de configuration.
Utilisez `.venv` (ce nom est déjà ignoré par Git).
# fase
