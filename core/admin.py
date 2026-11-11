from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import (
    Actualite, ArchiveItem, ArchivePhoto, BatExercice, Citation, Course, CourseFile,
    Delegue, MarketplaceItem, Promotion, Responsable, SiteConfig,
)

admin.site.site_header = "Administration FASE · UPC"
admin.site.site_title = "Administration FASE"
admin.site.index_title = "Gestion du site de la FASE"


@admin.register(SiteConfig)
class SiteConfigAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Citation)
class CitationAdmin(ModelAdmin):
    list_display = ("auteur", "texte", "actif", "ordre")
    list_editable = ("actif", "ordre")


class DelegueInline(admin.TabularInline):
    model = Delegue
    extra = 0


@admin.register(Promotion)
class PromotionAdmin(ModelAdmin):
    list_display = ("code", "nom", "annee_academique", "ordre", "actif")
    list_editable = ("ordre", "actif")
    inlines = [DelegueInline]


@admin.register(Responsable)
class ResponsableAdmin(ModelAdmin):
    list_display = ("nom", "fonction", "categorie", "ordre", "actif")
    list_filter = ("categorie", "actif")
    list_editable = ("ordre", "actif")
    search_fields = ("nom", "fonction")


class CourseFileInline(admin.TabularInline):
    model = CourseFile
    extra = 1


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ("code", "titre", "promotion", "semestre", "prof", "actif")
    list_filter = ("promotion", "semestre", "actif")
    search_fields = ("code", "titre", "prof")
    inlines = [CourseFileInline]


@admin.register(BatExercice)
class BatExerciceAdmin(ModelAdmin):
    list_display = ("titre", "type", "promotion", "date_ajout")
    list_filter = ("type", "promotion")
    search_fields = ("titre",)


@admin.action(description="Archiver (retirer de l'accueil)")
def archiver(modeladmin, request, queryset):
    count = 0
    for actu in queryset.filter(archivee=False):
        ArchiveItem.objects.create(
            titre=actu.titre,
            type="evenement" if actu.type == "Événement" else "communique",
            annee_academique=actu.annee_academique,
            date=actu.date,
            description=actu.texte,
            vignette=actu.image.name if actu.image else "",
            actualite=actu,
        )
        actu.archivee = True
        actu.save(update_fields=["archivee"])
        count += 1
    modeladmin.message_user(request, f"{count} actualité(s) archivée(s).")


@admin.action(description="Restaurer sur l'accueil")
def restaurer(modeladmin, request, queryset):
    for actu in queryset.filter(archivee=True):
        ArchiveItem.objects.filter(actualite=actu).delete()
        actu.archivee = False
        actu.save(update_fields=["archivee"])
    modeladmin.message_user(request, "Actualité(s) restaurée(s) sur l'accueil.")


@admin.register(Actualite)
class ActualiteAdmin(ModelAdmin):
    list_display = ("titre", "type", "date", "archivee")
    list_filter = ("type", "archivee", "annee_academique")
    search_fields = ("titre", "texte")
    actions = [archiver, restaurer]


class ArchivePhotoInline(admin.TabularInline):
    model = ArchivePhoto
    extra = 1


@admin.register(ArchiveItem)
class ArchiveItemAdmin(ModelAdmin):
    list_display = ("titre", "type", "annee_academique", "date")
    list_filter = ("annee_academique", "type")
    search_fields = ("titre", "description")
    inlines = [ArchivePhotoInline]


@admin.register(MarketplaceItem)
class MarketplaceItemAdmin(ModelAdmin):
    list_display = ("titre", "type", "vendeur_nom", "prix", "disponible")
    list_filter = ("type", "disponible")
    list_editable = ("disponible",)
