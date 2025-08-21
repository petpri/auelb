import csv
from django.core.management.base import BaseCommand
from app_auelb.models import Kunde  # <--- ersetze "deineapp" mit deinem App-Namen


class Command(BaseCommand):
    help = "Importiert Kunden aus einer CSV-Datei in die Datenbank"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Pfad zur CSV-Datei")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        with open(csv_file, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                print(row.keys())   # zeigt dir die exakten Spaltennamen
                obj, created = Kunde.objects.update_or_create(
                    kundennummer=int(row["kundennummer"]),
                    defaults={"kundenname": row["kundenname"]},
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"{obj} hinzugefügt"))
                else:
                    self.stdout.write(self.style.WARNING(f"{obj} aktualisiert"))