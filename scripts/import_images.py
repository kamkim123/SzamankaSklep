import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Szamanka.settings")
django.setup()

import csv
import requests
import os

os.makedirs("downloads", exist_ok=True)

with open("/Users/lena/Desktop/products-photos.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row["photo"]  # nazwa kolumny w CSV z linkami do zdjęć
        filename = url.split("/")[-1]
        filepath = os.path.join("downloads", filename)
        r = requests.get(url)
        if r.status_code == 200:
            with open(filepath, "wb") as img_file:
                img_file.write(r.content)
            print(f"Pobrano {filename}")
        else:
            print(f"Błąd pobierania {url}")