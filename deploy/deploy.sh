#!/bin/bash
# Mise à jour du site. À lancer depuis la racine du projet, environnement virtuel activé :
#   bash deploy/deploy.sh
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Dépendances"
pip install -r requirements.txt --quiet

echo "==> Sauvegarde de la base avant mise à jour"
python manage.py backup_db --keep 30

echo "==> Migrations"
python manage.py migrate --noinput

echo "==> Fichiers statiques"
python manage.py collectstatic --noinput --clear > /dev/null

echo "==> Contrôle de sécurité"
python manage.py check --deploy || true

echo "Terminé. Redémarrez l'application (Reload, restart du service ou redéploiement)."
