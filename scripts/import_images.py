import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Szamanka.settings")
django.setup()

import os
import csv
import requests

# folder docelowy - Pulpit
downloads_dir = "/Users/lena/Desktop/downloads"
os.makedirs(downloads_dir, exist_ok=True)

with open("/Users/lena/Desktop/products-photos.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row["photo"]  # nazwa kolumny z linkami w CSV
        filename = url.split("/")[-1]
        filepath = os.path.join(downloads_dir, filename)
        r = requests.get(url)
        if r.status_code == 200:
            with open(filepath, "wb") as img_file:
                img_file.write(r.content)
            print(f"Pobrano {filename}")
        else:
            print(f"Błąd pobierania {url}")