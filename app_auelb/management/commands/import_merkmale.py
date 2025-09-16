import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from app_auelb.models import Merkmale, Material


class Command(BaseCommand):
    help = "Importiert Merkmale aus einer CSV-Datei in die Datenbank"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Pfad zur CSV-Datei, z.B. merkmale.csv"
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        with open(csv_file, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                try:
                    # Material-Objekt holen
                    material = Material.objects.get(materialnummer=int(row["materialnummer"]))
                    
                    obj, created = Merkmale.objects.update_or_create(
                        materialnummer=material,
                        defaults={
                            "m_durchmesser": Decimal(row["m_durchmesser"]),
                            "m_gewicht": Decimal(row["m_gewicht"]),
                        },
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"{obj} hinzugefügt"))
                    else:
                        self.stdout.write(self.style.WARNING(f"{obj} aktualisiert"))

                except Material.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f"Material mit Nummer {row['materialnummer']} existiert nicht"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Fehler bei Zeile {row}: {e}"
                    ))
