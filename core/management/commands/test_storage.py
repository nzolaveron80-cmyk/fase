from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Teste l'envoi, l'adresse publique et la suppression d'un fichier."

    def handle(self, *args, **options):
        self.stdout.write(f"Stockage utilisé : {default_storage.__class__.__name__}")
        self.stdout.write(f"MEDIA_URL : {settings.MEDIA_URL}")
        try:
            nom = default_storage.save("diagnostic/test.txt", ContentFile(b"ok"))
            self.stdout.write(self.style.SUCCESS(f"Envoi OK : {default_storage.url(nom)}"))
            default_storage.delete(nom)
            self.stdout.write(self.style.SUCCESS("Suppression OK"))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"ECHEC : {type(exc).__name__} : {exc}"))