FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collecte des fichiers statiques pendant la construction (clé factice, non utilisée en production)
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput

# Cloud Run fournit le port dans la variable PORT
CMD sh -c "python manage.py migrate --noinput && gunicorn fase.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 60"
