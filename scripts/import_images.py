import os
import csv
import requests

downloads_dir = "/Users/lena/Desktop/downloads"
os.makedirs(downloads_dir, exist_ok=True)

csv_path = "/Users/lena/Desktop/products_photos.csv"

print("SKRYPT STARTUJE")

with open(csv_path, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=";")
    print(reader.fieldnames)  # możesz zostawić do sprawdzenia

    for row in reader:
        url = row["photo"]  # TERAZ zadziała
        filename = url.split("/")[-1]
        filepath = os.path.join(downloads_dir, filename)

        r = requests.get(url)
        if r.status_code == 200:
            with open(filepath, "wb") as img_file:
                img_file.write(r.content)
            print(f"Pobrano {filename}")
        else:
            print(f"Błąd pobierania {url}")