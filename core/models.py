from django.db import models
from django.utils import timezone


def annee_academique_courante():
    """Ex. 2026-2027 à partir de septembre 2026, sinon 2025-2026."""
    today = timezone.localdate()
    debut = today.year if today.month >= 9 else today.year - 1
    return f"{debut}-{debut + 1}"


class SiteConfig(models.Model):
    """Configuration unique du site (une seule ligne, pk=1)."""

    nom = models.CharField(
        "nom de la faculté", max_length=200,
        default="Faculté d'Administration des Affaires et Sciences Économiques",
    )
    titre = models.CharField(max_length=200, default="FASE · Université Protestante au Congo")
    devise = models.CharField(max_length=120, default="Vérité, Foi, Liberté")
    presidente = models.CharField("présidente de la FASE", max_length=120, blank=True)
    citation_presidente = models.CharField("citation de la présidente", max_length=200, blank=True)
    mot_presidente = models.TextField("mot de la présidente", blank=True)
    photo_presidente = models.ImageField(upload_to="site/", blank=True)
    adresse = models.CharField(max_length=255, default="Avenue du Centenaire, C. Lingwala, Kinshasa - RDC")
    permanence = models.CharField(max_length=120, default="Lundi au samedi : 08h00 - 16h00")
    email = models.EmailField(default="contact.fase@upc.cd")
    telephone = models.CharField(max_length=40, blank=True)
    email_secretariat = models.EmailField(blank=True)
    telephone_secretariat = models.CharField(max_length=40, blank=True)

    class Meta:
        verbose_name = "configuration du site"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.nom


class Citation(models.Model):
    texte = models.TextField()
    auteur = models.CharField(max_length=120)
    fonction = models.CharField(max_length=160, blank=True)
    actif = models.BooleanField(default=True)
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "id"]
        verbose_name = "citation d'accueil"
        verbose_name_plural = "citations d'accueil"

    def __str__(self):
        return f"{self.auteur} : {self.texte[:50]}"


class Promotion(models.Model):
    code = models.CharField("code", max_length=10, unique=True, help_text="Ex. L1, L2, M1, M2")
    nom = models.CharField(max_length=200, blank=True)
    annee_academique = models.CharField(max_length=20, blank=True)
    ordre = models.PositiveSmallIntegerField(default=0)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordre", "code"]

    def __str__(self):
        return self.code


class Delegue(models.Model):
    ROLES = [("chef", "Chef de promotion"), ("adjoint", "Adjoint")]

    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name="delegues")
    role = models.CharField(max_length=10, choices=ROLES, default="chef")
    nom = models.CharField(max_length=120)
    photo = models.ImageField(upload_to="delegues/", blank=True)
    message = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=40, blank=True)
    afficher_contact = models.BooleanField(default=False)

    class Meta:
        ordering = ["promotion", "role"]

    def __str__(self):
        return f"{self.get_role_display()} {self.promotion} : {self.nom}"


class Responsable(models.Model):
    CATEGORIES = [
        ("autorites", "Autorités"),
        ("decanat", "Décanat"),
        ("gouvernement", "Gouvernement facultaire"),
        ("departements", "Départements"),
        ("administration", "Administration"),
    ]

    categorie = models.CharField(max_length=20, choices=CATEGORIES, default="decanat")
    fonction = models.CharField(max_length=160)
    nom = models.CharField(max_length=120)
    titre_academique = models.CharField(max_length=80, blank=True)
    photo = models.ImageField(upload_to="responsables/", blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=40, blank=True)
    bureau = models.CharField(max_length=120, blank=True)
    biographie = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    ordre = models.PositiveSmallIntegerField(default=0)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["categorie", "ordre", "nom"]

    def __str__(self):
        return f"{self.fonction} : {self.nom}"


class Course(models.Model):
    SEMESTRES = [("Semestre 1", "Semestre 1"), ("Semestre 2", "Semestre 2")]

    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name="cours")
    semestre = models.CharField(max_length=20, choices=SEMESTRES, default="Semestre 1")
    code = models.CharField("code du cours", max_length=20)
    titre = models.CharField(max_length=200)
    prof = models.CharField("enseignant", max_length=120, blank=True)
    horaire = models.CharField("horaire et salle", max_length=160, blank=True)
    credits = models.PositiveSmallIntegerField("crédits", default=0)
    lien_externe = models.URLField(blank=True)
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["promotion", "semestre", "code"]

    def __str__(self):
        return f"{self.code} · {self.titre} ({self.promotion})"


class CourseFile(models.Model):
    cours = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="fichiers")
    nom = models.CharField(max_length=200, blank=True)
    fichier = models.FileField(upload_to="cours/")
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom or self.fichier.name


class BatExercice(models.Model):
    TYPES = [("Exercice", "Exercice"), ("BAT", "BAT")]

    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name="bat_exercices")
    type = models.CharField(max_length=10, choices=TYPES, default="Exercice")
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to="bat/")
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_ajout"]
        verbose_name = "BAT / exercice"
        verbose_name_plural = "BAT et exercices"

    def __str__(self):
        return f"{self.type} · {self.titre} ({self.promotion})"


class Actualite(models.Model):
    TYPES = [("Événement", "Événement"), ("Communiqué", "Communiqué")]

    type = models.CharField(max_length=20, choices=TYPES, default="Communiqué")
    date = models.DateField(default=timezone.localdate)
    titre = models.CharField(max_length=200)
    texte = models.TextField()
    image = models.ImageField(upload_to="actus/", blank=True)
    auteur = models.CharField(max_length=120, blank=True)
    annee_academique = models.CharField(max_length=20, default=annee_academique_courante)
    archivee = models.BooleanField("archivée", default=False,
                                   help_text="Si coché, l'actualité n'apparaît plus à l'accueil.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "actualité"
        verbose_name_plural = "actualités"

    def __str__(self):
        return self.titre


class ArchiveItem(models.Model):
    TYPES = [
        ("article", "Article"),
        ("communique", "Communiqué"),
        ("evenement", "Événement"),
        ("album", "Album photo"),
        ("document", "Document officiel"),
    ]

    titre = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPES, default="document")
    annee_academique = models.CharField(max_length=20, default=annee_academique_courante)
    date = models.DateField(default=timezone.localdate)
    description = models.TextField(blank=True)
    vignette = models.ImageField(upload_to="archives/", blank=True)
    fichier = models.FileField(upload_to="archives/", blank=True)
    actualite = models.OneToOneField(
        Actualite, on_delete=models.SET_NULL, null=True, blank=True, related_name="archive"
    )

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "archive"
        verbose_name_plural = "archives"

    def __str__(self):
        return f"{self.titre} ({self.annee_academique})"


class ArchivePhoto(models.Model):
    archive = models.ForeignKey(ArchiveItem, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="archives/photos/")
    legende = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.legende or self.image.name


class MarketplaceItem(models.Model):
    TYPES = [("produit", "Produit"), ("service", "Service")]

    titre = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPES, default="produit")
    description = models.TextField()
    photo = models.ImageField(upload_to="marketplace/", blank=True)
    vendeur_nom = models.CharField(max_length=120)
    vendeur_whatsapp = models.CharField("WhatsApp du vendeur", max_length=30,
                                        help_text="Format international, ex. +243810000000")
    vendeur_promotion = models.CharField(max_length=60, blank=True, help_text="Ex. L2 Économie")
    prix = models.CharField(max_length=60, blank=True, help_text="Ex. 15 $, Sur devis, Négociable")
    disponible = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_ajout"]

    def __str__(self):
        return self.titre
