from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", views.home, name="accueil"),
    path("cours/", views.cours, name="cours"),
    path("responsables/", views.responsables, name="responsables"),
    path("bat-exercices/", views.bat_exercices, name="bat_exercices"),
    path("archives/", views.archives, name="archives"),
    path("marketplace/", views.marketplace, name="marketplace"),
    path("cgu/", views.legal, {"page": "cgu"}, name="cgu"),
    path("confidentialite/", views.legal, {"page": "confidentialite"}, name="confidentialite"),
    path("cookies/", views.legal, {"page": "cookies"}, name="cookies"),
    # Anciennes routes de l'application React : redirection permanente (301)
    path("actualites/", RedirectView.as_view(pattern_name="accueil", permanent=True)),
    path("galerie/", RedirectView.as_view(pattern_name="archives", permanent=True)),
]
