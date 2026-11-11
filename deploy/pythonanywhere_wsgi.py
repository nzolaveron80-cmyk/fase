# Contenu à coller dans l'onglet Web > "WSGI configuration file" sur PythonAnywhere.
# Remplacer VOTREPSEUDO par votre identifiant PythonAnywhere.
import os
import sys

PROJECT_PATH = "/home/VOTREPSEUDO/fase-django"
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fase.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
