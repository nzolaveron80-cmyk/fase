from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from .models import (
    Actualite, ArchiveItem, BatExercice, Citation, Course, MarketplaceItem,
    Promotion, Responsable,
)

SEMESTRES = ["Semestre 1", "Semestre 2"]


def home(request):
    filtre = request.GET.get("filtre", "tout")
    base = Actualite.objects.filter(archivee=False)
    counts = {
        "tout": base.count(),
        "evenements": base.filter(type="Événement").count(),
        "communiques": base.filter(type="Communiqué").count(),
    }
    actus = base
    if filtre == "evenements":
        actus = actus.filter(type="Événement")
    elif filtre == "communiques":
        actus = actus.filter(type="Communiqué")

    context = {
        "citations": Citation.objects.filter(actif=True)[:3],
        "actus": actus[:6],
        "filtre": filtre,
        "counts": counts,
        "promotions": Promotion.objects.filter(actif=True).prefetch_related("delegues"),
    }
    return render(request, "core/home.html", context)


def cours(request):
    promo = request.GET.get("promo", "")
    semestre = request.GET.get("semestre", "")
    q = request.GET.get("q", "").strip()

    qs = (Course.objects.filter(actif=True)
          .select_related("promotion")
          .prefetch_related("fichiers"))
    if promo:
        qs = qs.filter(promotion__code=promo)
    if semestre in SEMESTRES:
        qs = qs.filter(semestre=semestre)
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(code__icontains=q) | Q(prof__icontains=q))

    return render(request, "core/cours.html", {
        "cours": qs,
        "promotions": Promotion.objects.filter(actif=True),
        "semestres": SEMESTRES,
        "promo": promo,
        "semestre": semestre,
        "q": q,
    })


def responsables(request):
    groupes = []
    for code, libelle in Responsable.CATEGORIES:
        items = list(Responsable.objects.filter(actif=True, categorie=code))
        if items:
            groupes.append((libelle, items))
    return render(request, "core/responsables.html", {"groupes": groupes})


def bat_exercices(request):
    promo = request.GET.get("promo", "")
    type_ = request.GET.get("type", "")
    qs = BatExercice.objects.select_related("promotion")
    if promo:
        qs = qs.filter(promotion__code=promo)
    if type_ in ("Exercice", "BAT"):
        qs = qs.filter(type=type_)
    return render(request, "core/bat_exercices.html", {
        "items": qs,
        "promotions": Promotion.objects.filter(actif=True),
        "promo": promo,
        "type": type_,
    })


def archives(request):
    annee = request.GET.get("annee", "")
    categorie = request.GET.get("categorie", "")
    q = request.GET.get("q", "").strip()

    qs = ArchiveItem.objects.prefetch_related("photos")
    if annee:
        qs = qs.filter(annee_academique=annee)
    if categorie:
        qs = qs.filter(type=categorie)
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(description__icontains=q))

    annees = (ArchiveItem.objects.order_by("-annee_academique")
              .values_list("annee_academique", flat=True).distinct())
    return render(request, "core/archives.html", {
        "items": qs,
        "annees": annees,
        "categories": ArchiveItem.TYPES,
        "annee": annee,
        "categorie": categorie,
        "q": q,
    })


def marketplace(request):
    type_ = request.GET.get("type", "")
    qs = MarketplaceItem.objects.filter(disponible=True)
    if type_ in ("produit", "service"):
        qs = qs.filter(type=type_)
    return render(request, "core/marketplace.html", {"items": qs, "type": type_})


LEGAL_PAGES = {
    "cgu": "Conditions générales d'utilisation",
    "confidentialite": "Politique de confidentialité",
    "cookies": "Politique de cookies",
}


def legal(request, page):
    if page not in LEGAL_PAGES:
        raise Http404
    return render(request, f"core/legal/{page}.html", {"titre": LEGAL_PAGES[page]})
