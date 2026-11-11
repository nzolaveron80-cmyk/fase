import os
import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crée une copie de la base SQLite et supprime les plus anciennes."

    def add_arguments(self, parser):
        parser.add_argument("--keep", type=int, default=14,
                            help="Nombre de sauvegardes à conserver (défaut : 14)")

    def handle(self, *args, **options):
        if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
            self.stdout.write(
                "Base non SQLite : utilisez les sauvegardes de votre hébergeur "
                "(Cloud SQL gère ses sauvegardes automatiques si elles sont activées)."
            )
            return

        db_path = Path(settings.DATABASES["default"]["NAME"])
        backup_dir = Path(os.environ.get("DJANGO_BACKUP_DIR", Path(settings.BASE_DIR) / "backups"))
        backup_dir.mkdir(parents=True, exist_ok=True)

        target = backup_dir / f"db-{datetime.now():%Y%m%d-%H%M%S}.sqlite3"

        # API de sauvegarde SQLite : copie cohérente même pendant une utilisation du site
        src = sqlite3.connect(db_path)
        dst = sqlite3.connect(target)
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()

        backups = sorted(backup_dir.glob("db-*.sqlite3"))
        for old in backups[:-options["keep"]]:
            old.unlink()

        self.stdout.write(self.style.SUCCESS(f"Sauvegarde créée : {target}"))
