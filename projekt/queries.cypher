// Projekt: Graf zakupowy z rekomendacjami – zapytania

// Q1 [agregacja] – 10 najpopularniejszych produktów wg liczby kupujących wraz z przychodem.
MATCH (c:Customer)-[b:BOUGHT]->(p:Product)-[:BELONGS_TO]->(cat:Category)
RETURN p.product_id AS id, p.name AS product, cat.name AS category,
       count(DISTINCT c) AS buyers,
       round(sum(b.quantity * p.price), 2) AS revenue
ORDER BY buyers DESC, revenue DESC
LIMIT 10;

// Q2 [agregacja] – Liczba transakcji, sztuk i przychód w każdej kategorii.
MATCH (:Customer)-[b:BOUGHT]->(p:Product)-[:BELONGS_TO]->(cat:Category)
RETURN cat.name AS category, count(b) AS transactions,
       sum(b.quantity) AS units,
       round(sum(b.quantity * p.price), 2) AS revenue
ORDER BY revenue DESC;

// Q3 [agregacja (HAVING)] – Średnia ocena produktów każdej marki – tylko marki z co najmniej 50 ocenami.
MATCH (:Customer)-[b:BOUGHT]->(:Product)-[:MADE_BY]->(br:Brand)
WITH br.name AS brand, round(avg(b.rating), 2) AS avg_rating, count(b) AS ratings
WHERE ratings >= 50
RETURN brand, avg_rating, ratings
ORDER BY avg_rating DESC;

// Q4 [agregacja] – Liczba klientów, średnie wydatki na klienta i łączny przychód wg miasta.
MATCH (city:City)<-[:LIVES_IN]-(c:Customer)-[b:BOUGHT]->(p:Product)
WITH city, c, sum(b.quantity * p.price) AS spent
RETURN city.name AS city, count(c) AS customers,
       round(avg(spent), 2) AS avg_spent_per_customer,
       round(sum(spent), 2) AS revenue
ORDER BY revenue DESC;

// Q5 [agregacja + collect] – 5 klientów o najwyższych wydatkach z listą kupowanych kategorii.
MATCH (c:Customer)-[b:BOUGHT]->(p:Product)-[:BELONGS_TO]->(cat:Category)
RETURN c.customer_id AS id, c.name AS customer,
       round(sum(b.quantity * p.price), 2) AS spent,
       count(b) AS purchases,
       collect(DISTINCT cat.name) AS categories
ORDER BY spent DESC
LIMIT 5;

// Q6 [wzorzec ścieżki] – „Klienci, którzy kupili produkt P001, kupili również” – 5 produktów z największą liczbą wspólnych klientów.
MATCH (:Product {product_id: "P001"})<-[:BOUGHT]-(c:Customer)-[:BOUGHT]->(other:Product)
WHERE other.product_id <> "P001"
RETURN other.product_id AS id, other.name AS product,
       count(DISTINCT c) AS common_customers
ORDER BY common_customers DESC, id
LIMIT 5;

// Q7 [wzorzec ścieżki (collaborative filtering)] – Rekomendacje dla klienta K072: produkty kupione przez klientów o podobnych zakupach, których K072 jeszcze nie ma.
MATCH (me:Customer {customer_id: "K072"})-[:BOUGHT]->(p:Product)<-[:BOUGHT]-(peer:Customer)
WITH me, peer, count(DISTINCT p) AS similarity
MATCH (peer)-[b:BOUGHT]->(rec:Product)
WHERE NOT (me)-[:BOUGHT]->(rec) AND b.rating >= 4
MATCH (rec)-[:BELONGS_TO]->(cat:Category)
RETURN rec.product_id AS id, rec.name AS product, cat.name AS category,
       sum(similarity) AS score, count(DISTINCT peer) AS peers
ORDER BY score DESC, peers DESC
LIMIT 5;

// Q8 [shortestPath] – Najkrótszy łańcuch obserwowania (FOLLOWS) od klienta K072 do klienta K031.
MATCH path = shortestPath(
  (a:Customer {customer_id: "K072"})-[:FOLLOWS*..10]->(b:Customer {customer_id: "K031"}))
RETURN [n IN nodes(path) | n.customer_id + " " + n.name] AS chain,
       length(path) AS hops;

// Q9 [ścieżka o zmiennej długości] – Zasięg wpływu: 5 klientów, do których najwięcej osób dociera w 1–3 krokach FOLLOWS (influencerzy).
MATCH (influencer:Customer)<-[:FOLLOWS*1..3]-(fan:Customer)
WHERE fan <> influencer
RETURN influencer.customer_id AS id, influencer.name AS customer,
       count(DISTINCT fan) AS reach_3_hops
ORDER BY reach_3_hops DESC
LIMIT 5;

// Q10 [ścieżka o zmiennej długości] – Rekomendacje społeczne dla K072: produkty ocenione na 5 przez osoby obserwowane przez K072 w 1–2 krokach.
MATCH (me:Customer {customer_id: "K072"})-[:FOLLOWS*1..2]->(friend:Customer)-[b:BOUGHT]->(p:Product)
WHERE b.rating = 5 AND NOT (me)-[:BOUGHT]->(p) AND friend <> me
RETURN p.product_id AS id, p.name AS product,
       collect(DISTINCT friend.name) AS recommended_by
ORDER BY size(recommended_by) DESC, id
LIMIT 5;

// Q11 [agregacja (HAVING)] – Klienci kupujący w co najmniej 5 kategoriach (kandydaci do cross-sellingu).
MATCH (c:Customer)-[:BOUGHT]->(:Product)-[:BELONGS_TO]->(cat:Category)
WITH c, count(DISTINCT cat) AS n_categories, collect(DISTINCT cat.name) AS categories
WHERE n_categories >= 5
RETURN c.customer_id AS id, c.name AS customer, n_categories, categories
ORDER BY n_categories DESC, id;

// Q12 [agregacja] – Kwartalna liczba transakcji i przychód (trend sprzedaży).
MATCH (:Customer)-[b:BOUGHT]->(p:Product)
WITH b.date.year AS year, b.date.quarter AS quarter, b, p
RETURN year, quarter, count(b) AS transactions,
       round(sum(b.quantity * p.price), 2) AS revenue
ORDER BY year, quarter;

// Q13 [wyszukujące (OPTIONAL MATCH)] – Produkty o najsłabszej sprzedaży – kupione przez mniej niż 4 klientów (kandydaci do przeceny lub wycofania).
MATCH (p:Product)-[:BELONGS_TO]->(cat:Category)
OPTIONAL MATCH (c:Customer)-[:BOUGHT]->(p)
WITH p, cat, count(c) AS buyers
WHERE buyers < 4
RETURN p.product_id AS id, p.name AS product, cat.name AS category,
       p.price AS price, buyers
ORDER BY buyers, category;
