import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file():
    """Charge le fichier .env (s'il existe) sans écraser les variables déjà définies."""
    env_path = BASE_DIR / ".env"
    # is_file() : ignore un dossier nommé .env (ex. un environnement virtuel)
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [v.strip() for v in os.environ.get(name, default).split(",") if v.strip()]


load_env_file()

# ---------------------------------------------------------------- Sécurité
# DEBUG est désactivé par défaut : il faut le mettre à 1 explicitement en local.
DEBUG = env_bool("DJANGO_DEBUG", False)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-only-insecure-key-ne-pas-utiliser-en-production"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY doit être défini en production (voir .env.example)."
        )

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # PythonAnywhere termine le HTTPS en amont : Django doit faire confiance à l'en-tête
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    SECURE_HSTS_SECONDS = 3600
    X_FRAME_OPTIONS = "DENY"

    # Non applicables sur un sous-domaine pythonanywhere.com (domaine appartenant à PythonAnywhere) :
    # - security.W005 / W021 : on ne contrôle pas les sous-domaines ni la liste de préchargement.
    # Si vous passez à un domaine personnel (ex. fase.upc.cd), retirez cette ligne et
    # envisagez SECURE_HSTS_INCLUDE_SUBDOMAINS après avoir vérifié que tous les sous-domaines sont en HTTPS.
    SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]

# ---------------------------------------------------------------- Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "fase.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "fase.wsgi.application"

# ---------------------------------------------------------------- Base de données
# Le fichier SQLite doit être dans un dossier persistant (ex. ~/fase-django sur PythonAnywhere)
DATABASE_URL = os.environ.get("DATABASE_URL", "")
CLOUD_SQL_CONNECTION_NAME = os.environ.get("CLOUD_SQL_CONNECTION_NAME", "")

if CLOUD_SQL_CONNECTION_NAME:
    # Google Cloud SQL via le socket Unix monté par Cloud Run
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASSWORD"],
            "HOST": f"/cloudsql/{CLOUD_SQL_CONNECTION_NAME}",
            "CONN_MAX_AGE": 600,
        }
    }
elif DATABASE_URL:
    # PostgreSQL (Supabase) : l'adresse est fournie par l'hébergeur
    import dj_database_url
    try:
        DATABASES = {
            "default": dj_database_url.parse(
                DATABASE_URL, conn_max_age=int(os.environ.get("DB_CONN_MAX_AGE", "60"))
            )
        }
    except Exception:
        # Ne pas afficher l'URL (elle contient le mot de passe)
        raise ImproperlyConfigured(
            "DATABASE_URL est invalide. ..."
        ) from None

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------- Internationalisation
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Kinshasa"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------- Fichiers statiques et médias
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("DJANGO_MEDIA_ROOT", BASE_DIR / "media"))
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT_URL", "")
S3_KEY = os.environ.get("S3_ACCESS_KEY_ID", "")
S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY", "")
S3_DOMAIN = os.environ.get("S3_PUBLIC_DOMAIN", "")

# Stockage S3 (Supabase) activé seulement si toutes les variables sont présentes
USE_S3 = all([S3_BUCKET, S3_ENDPOINT, S3_KEY, S3_SECRET, S3_DOMAIN])
if USE_S3:
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3.S3Storage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
    }
    AWS_STORAGE_BUCKET_NAME = S3_BUCKET
    AWS_S3_ENDPOINT_URL = S3_ENDPOINT
    AWS_S3_REGION_NAME = os.environ.get("S3_REGION", "eu-west-3")
    AWS_ACCESS_KEY_ID = S3_KEY
    AWS_SECRET_ACCESS_KEY = S3_SECRET
    AWS_S3_CUSTOM_DOMAIN = S3_DOMAIN
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    MEDIA_URL = f"https://{S3_DOMAIN}/"

# Fichiers servis par Django seulement si le stockage S3 n'est pas configuré
SERVE_MEDIA_LOCALLY = not USE_S3

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
