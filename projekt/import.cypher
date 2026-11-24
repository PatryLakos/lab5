// =====================================================================
// Projekt: Graf zakupowy z rekomendacjami – import danych (LOAD CSV)
// Pliki CSV leżą w projekt/data (katalog importu kontenera graphdb_projekt)
// Uruchomienie: Neo4j Browser http://localhost:7475  lub  uv run projekt.py
// =====================================================================

// 0. Czyszczenie grafu (pozwala bezpiecznie powtórzyć import)
MATCH (n) DETACH DELETE n;

// 1. Ograniczenia unikatowości (tworzą też indeksy)
CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE;
CREATE CONSTRAINT product_id  IF NOT EXISTS FOR (p:Product)  REQUIRE p.product_id  IS UNIQUE;
CREATE CONSTRAINT category_id IF NOT EXISTS FOR (c:Category) REQUIRE c.category_id IS UNIQUE;
CREATE CONSTRAINT brand_id    IF NOT EXISTS FOR (b:Brand)    REQUIRE b.brand_id    IS UNIQUE;
CREATE CONSTRAINT city_name   IF NOT EXISTS FOR (c:City)     REQUIRE c.name        IS UNIQUE;

// 2. Węzły słownikowe
LOAD CSV WITH HEADERS FROM "file:///categories.csv" AS row
MERGE (:Category {category_id: row.category_id, name: row.name});

LOAD CSV WITH HEADERS FROM "file:///brands.csv" AS row
MERGE (:Brand {brand_id: row.brand_id, name: row.name});

LOAD CSV WITH HEADERS FROM "file:///cities.csv" AS row
MERGE (:City {name: row.city, voivodeship: row.voivodeship});

// 3. Produkty + relacje BELONGS_TO i MADE_BY
LOAD CSV WITH HEADERS FROM "file:///products.csv" AS row
MATCH (cat:Category {category_id: row.category_id})
MATCH (b:Brand {brand_id: row.brand_id})
MERGE (p:Product {product_id: row.product_id})
SET p.name = row.name, p.price = toFloat(row.price)
MERGE (p)-[:BELONGS_TO]->(cat)
MERGE (p)-[:MADE_BY]->(b);

// 4. Klienci + relacja LIVES_IN
LOAD CSV WITH HEADERS FROM "file:///customers.csv" AS row
MATCH (city:City {name: row.city})
MERGE (c:Customer {customer_id: row.customer_id})
SET c.name = row.name, c.age = toInteger(row.age), c.registered = date(row.registered)
MERGE (c)-[:LIVES_IN]->(city);

// 5. Zakupy – relacja BOUGHT z właściwościami (ilość, data, ocena)
LOAD CSV WITH HEADERS FROM "file:///orders.csv" AS row
MATCH (c:Customer {customer_id: row.customer_id})
MATCH (p:Product {product_id: row.product_id})
CREATE (c)-[:BOUGHT {quantity: toInteger(row.quantity),
                     date: date(row.date),
                     rating: toInteger(row.rating)}]->(p);

// 6. Sieć społeczna – relacja FOLLOWS między klientami
LOAD CSV WITH HEADERS FROM "file:///follows.csv" AS row
MATCH (a:Customer {customer_id: row.follower_id})
MATCH (b:Customer {customer_id: row.followed_id})
MERGE (a)-[:FOLLOWS]->(b);

// 7. Weryfikacja
MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY cnt DESC;
MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS cnt ORDER BY cnt DESC;
