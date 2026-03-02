import os
import csv
import requests
from django.core.files.base import ContentFile

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Szamanka.settings")
django.setup()

from products.models import Product


CSV_PATH = "/Users/lena/Desktop/products_photos.csv"

print("START IMPORTU ZDJĘĆ\n")

added = 0
skipped_existing = 0
not_found = 0
errors = 0

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=";")

    for row in reader:
        ean = row["ean"]
        image_url = row["photo"]

        if not ean or not image_url:
            continue

        try:
            product = Product.objects.filter(product_code=ean).first()

            if not product:
                print(f"❌ Nie znaleziono produktu z EAN: {ean}")
                not_found += 1
                continue

            if product.product_image_file:
                print(f"⏭ Produkt {product.product_name} ma już zdjęcie — pomijam")
                skipped_existing += 1
                continue

            response = requests.get(image_url, timeout=10)

            if response.status_code != 200:
                print(f"⚠️ Błąd pobierania: {image_url}")
                errors += 1
                continue

            filename = image_url.split("/")[-1]

            product.product_image_file.save(
                filename,
                ContentFile(response.content),
                save=True
            )

            print(f"✅ Dodano zdjęcie do: {product.product_name}")
            added += 1

        except Exception as e:
            print(f"🔥 Błąd przy EAN {ean}: {e}")
            errors += 1


print("\n--- PODSUMOWANIE ---")
print(f"Dodano zdjęć: {added}")
print(f"Pominięto (już miały): {skipped_existing}")
print(f"Nie znaleziono produktu: {not_found}")
print(f"Błędy: {errors}")