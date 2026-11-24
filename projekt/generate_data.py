"""Generator danych dla projektu „Graf zakupowy z rekomendacjami”.

Dane są syntetyczne (wygenerowane tym skryptem, seed=42), więc nie obowiązuje
licencja zewnętrzna. Klienci mają preferowane kategorie, dzięki czemu wzorce
zakupowe (i rekomendacje) nie są czysto losowe.
Wynik: pliki CSV w katalogu data/.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

CATEGORIES = {
    "Elektronika": ["Słuchawki", "Smartwatch", "Powerbank", "Głośnik", "Kamera", "Router", "Klawiatura", "Mysz"],
    "Książki": ["Kryminał", "Fantastyka", "Poradnik Python", "Biografia", "Reportaż", "Atlas", "Komiks"],
    "Sport": ["Hantle", "Mata do jogi", "Rower", "Piłka", "Rakieta", "Kask", "Bidon"],
    "Dom i ogród": ["Lampa", "Doniczka", "Kosiarka", "Grill", "Poduszka", "Koc", "Czajnik"],
    "Moda": ["Kurtka", "Buty", "Plecak", "Czapka", "Bluza", "Zegarek"],
    "Zabawki": ["Klocki", "Puzzle", "Gra planszowa", "Lalka", "Samochodzik"],
    "Uroda": ["Krem", "Perfumy", "Szampon", "Suszarka"],
    "Spożywcze": ["Kawa", "Herbata", "Czekolada", "Oliwa"],
}
BRANDS = ["Nordix", "Volta", "Sportaro", "Domeo", "Kreda", "Lumen", "Fiora",
          "Polmark", "Bitwave", "Arctis", "Zielono", "Kodama"]
CITIES = [("Lublin", "lubelskie"), ("Warszawa", "mazowieckie"), ("Kraków", "małopolskie"),
          ("Gdańsk", "pomorskie"), ("Wrocław", "dolnośląskie"), ("Poznań", "wielkopolskie"),
          ("Rzeszów", "podkarpackie"), ("Zamość", "lubelskie")]
FIRST = ["Anna", "Piotr", "Kasia", "Tomasz", "Ola", "Michał", "Ewa", "Jakub", "Zofia", "Marek",
         "Julia", "Paweł", "Natalia", "Kamil", "Magda", "Bartek", "Ilona", "Adam", "Wiktoria", "Szymon"]
LAST = ["Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kamiński", "Lewandowski", "Zieliński",
        "Szymański", "Woźniak", "Dąbrowski", "Kozłowski", "Mazur", "Krawczyk", "Piątek"]
PRICE_RANGE = {"Elektronika": (49, 1299), "Książki": (19, 89), "Sport": (25, 2499),
               "Dom i ogród": (29, 1899), "Moda": (39, 699), "Zabawki": (19, 399),
               "Uroda": (15, 399), "Spożywcze": (9, 79)}


def write(name, header, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} wierszy")


# --- kategorie, marki, miasta
write("categories.csv", ["category_id", "name"],
      [[f"C{i+1}", c] for i, c in enumerate(CATEGORIES)])
cat_id = {c: f"C{i+1}" for i, c in enumerate(CATEGORIES)}
write("brands.csv", ["brand_id", "name"], [[f"B{i+1}", b] for i, b in enumerate(BRANDS)])
write("cities.csv", ["city", "voivodeship"], CITIES)

# --- produkty (≥ 100)
products = []
pid = 1
for cat, items in CATEGORIES.items():
    for item in items:
        for _ in range(3 if cat in ("Elektronika", "Książki", "Sport", "Dom i ogród") else 2):
            brand = random.choice(BRANDS)
            lo, hi = PRICE_RANGE[cat]
            price = round(random.uniform(lo, hi), 2)
            products.append([f"P{pid:03d}", f"{item} {brand} {random.choice(['Basic', 'Pro', 'Max', 'Lite', 'Plus'])}",
                             round(price, 2), cat_id[cat], f"B{BRANDS.index(brand)+1}"])
            pid += 1
write("products.csv", ["product_id", "name", "price", "category_id", "brand_id"], products)
prod_by_cat = {}
for p in products:
    prod_by_cat.setdefault(p[3], []).append(p)

# --- klienci (≥ 100, główna etykieta)
customers = []
for i in range(1, 201):
    city = random.choice(CITIES)[0]
    first, last = random.choice(FIRST), random.choice(LAST)
    if first.endswith("a") and last.endswith("ski"):
        last = last[:-1] + "a"
    customers.append([f"K{i:03d}", f"{first} {last}",
                      random.randint(18, 70), city,
                      (date(2023, 1, 1) + timedelta(days=random.randint(0, 900))).isoformat()])
write("customers.csv", ["customer_id", "name", "age", "city", "registered"], customers)

# --- zakupy: każdy klient ma 1-2 ulubione kategorie (70% zakupów) + losowe
orders = []
start = date(2025, 1, 1)
for c in customers:
    fav = random.sample(list(prod_by_cat), k=random.choice([1, 2]))
    bought = set()
    for _ in range(random.randint(2, 12)):
        pool = prod_by_cat[random.choice(fav)] if random.random() < 0.7 else products
        p = random.choice(pool)
        if p[0] in bought:
            continue
        bought.add(p[0])
        rating = random.choices([1, 2, 3, 4, 5], weights=[3, 5, 15, 40, 37])[0]
        orders.append([c[0], p[0], random.choices([1, 2, 3], weights=[80, 15, 5])[0],
                       (start + timedelta(days=random.randint(0, 690))).isoformat(), rating])
write("orders.csv", ["customer_id", "product_id", "quantity", "date", "rating"], orders)

# --- sieć poleceń: kto kogo obserwuje (graf społeczny, skierowany)
follows = set()
for c in customers:
    for _ in range(random.randint(0, 3)):
        other = random.choice(customers)[0]
        if other != c[0]:
            follows.add((c[0], other))
write("follows.csv", ["follower_id", "followed_id"], sorted(follows))
