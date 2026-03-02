import csv
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import Product


class Command(BaseCommand):
    help = "Przypisuje zdjęcia do produktów na podstawie EAN"

    def handle(self, *args, **kwargs):
        CSV_PATH = "/Users/lena/Desktop/products_photos.csv"

        added = 0
        skipped_existing = 0
        not_found = 0
        errors = 0

        with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                ean = row.get("ean")
                image_url = row.get("photo")

                if not ean or not image_url:
                    continue

                product = Product.objects.filter(product_code=ean).first()

                if not product:
                    not_found += 1
                    continue

                if product.product_image_file:
                    skipped_existing += 1
                    continue

                try:
                    response = requests.get(image_url, timeout=10)
                    if response.status_code != 200:
                        errors += 1
                        continue

                    filename = image_url.split("/")[-1]

                    product.product_image_file.save(
                        filename,
                        ContentFile(response.content),
                        save=True
                    )

                    added += 1

                except Exception:
                    errors += 1

        self.stdout.write(self.style.SUCCESS("\n--- PODSUMOWANIE ---"))
        self.stdout.write(f"Dodano zdjęć: {added}")
        self.stdout.write(f"Pominięto (już miały): {skipped_existing}")
        self.stdout.write(f"Nie znaleziono produktu: {not_found}")
        self.stdout.write(f"Błędy: {errors}")