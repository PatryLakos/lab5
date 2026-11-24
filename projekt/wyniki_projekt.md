# Wyniki zapytań – projekt „Graf zakupowy z rekomendacjami”

## Węzły po imporcie

```cypher
MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY cnt DESC
```

| label    |   cnt |
|:---------|------:|
| Customer |   200 |
| Product  |   125 |
| Brand    |    12 |
| Category |     8 |
| City     |     8 |

## Relacje po imporcie

```cypher
MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS cnt ORDER BY cnt DESC
```

| type       |   cnt |
|:-----------|------:|
| BOUGHT     |  1233 |
| FOLLOWS    |   279 |
| LIVES_IN   |   200 |
| BELONGS_TO |   125 |
| MADE_BY    |   125 |

## Q1 [agregacja, W1]

10 najpopularniejszych produktów wg liczby kupujących wraz z przychodem.

```cypher
MATCH (c:Customer)-[b:BOUGHT]->(p:Product)-[:BELONGS_TO]->(cat:Category)
RETURN p.product_id AS id, p.name AS product, cat.name AS category,
       count(DISTINCT c) AS buyers,
       round(sum(b.quantity * p.price), 2) AS revenue
ORDER BY buyers DESC, revenue DESC
LIMIT 10
```

| id   | product                | category   |   buyers |   revenue |
|:-----|:-----------------------|:-----------|---------:|----------:|
| P119 | Kawa Zielono Pro       | Spożywcze  |       24 |   2327.7  |
| P116 | Suszarka Bitwave Basic | Uroda      |       22 |   6078    |
| P093 | Plecak Sportaro Plus   | Moda       |       22 |   1990.04 |
| P110 | Krem Nordix Plus       | Uroda      |       20 |   6515.04 |
| P117 | Suszarka Volta Max     | Uroda      |       20 |   5688.54 |
| P115 | Szampon Domeo Max      | Uroda      |       19 |   6975    |
| P114 | Szampon Kreda Max      | Uroda      |       19 |   5934    |
| P121 | Herbata Bitwave Basic  | Spożywcze  |       19 |    212.96 |
| P090 | Buty Arctis Basic      | Moda       |       18 |  11016.4  |
| P112 | Perfumy Sportaro Basic | Uroda      |       18 |   2447.55 |

## Q2 [agregacja, W1]

Liczba transakcji, sztuk i przychód w każdej kategorii.

```cypher
MATCH (:Customer)-[b:BOUGHT]->(p:Product)-[:BELONGS_TO]->(cat:Category)
RETURN cat.name AS category, count(b) AS transactions,
       sum(b.quantity) AS units,
       round(sum(b.quantity * p.price), 2) AS revenue
ORDER BY revenue DESC
```

| category    |   transactions |   units |   revenue |
|:------------|---------------:|--------:|----------:|
| Sport       |            150 |     185 |  270876   |
| Dom i ogród |            193 |     251 |  189519   |
| Elektronika |            177 |     210 |  135788   |
| Moda        |            157 |     192 |   59918.5 |
| Uroda       |            148 |     183 |   44379   |
| Zabawki     |            111 |     138 |   29025.5 |
| Książki     |            161 |     196 |   10389.9 |
| Spożywcze   |            136 |     173 |    7640.6 |

## Q3 [agregacja (HAVING), W4]

Średnia ocena produktów każdej marki – tylko marki z co najmniej 50 ocenami.

```cypher
MATCH (:Customer)-[b:BOUGHT]->(:Product)-[:MADE_BY]->(br:Brand)
WITH br.name AS brand, round(avg(b.rating), 2) AS avg_rating, count(b) AS ratings
WHERE ratings >= 50
RETURN brand, avg_rating, ratings
ORDER BY avg_rating DESC
```

| brand    |   avg_rating |   ratings |
|:---------|-------------:|----------:|
| Arctis   |         4.13 |       100 |
| Nordix   |         4.11 |       138 |
| Sportaro |         4.09 |       105 |
| Domeo    |         4.05 |       127 |
| Bitwave  |         4.05 |       135 |
| Fiora    |         4    |        98 |
| Zielono  |         3.98 |       131 |
| Volta    |         3.94 |       161 |
| Kreda    |         3.89 |        87 |
| Kodama   |         3.88 |        97 |

## Q4 [agregacja, W3]

Liczba klientów, średnie wydatki na klienta i łączny przychód wg miasta.

```cypher
MATCH (city:City)<-[:LIVES_IN]-(c:Customer)-[b:BOUGHT]->(p:Product)
WITH city, c, sum(b.quantity * p.price) AS spent
RETURN city.name AS city, count(c) AS customers,
       round(avg(spent), 2) AS avg_spent_per_customer,
       round(sum(spent), 2) AS revenue
ORDER BY revenue DESC
```

| city     |   customers |   avg_spent_per_customer |   revenue |
|:---------|------------:|-------------------------:|----------:|
| Rzeszów  |          28 |                  4446.66 |  124507   |
| Wrocław  |          29 |                  3806.74 |  110395   |
| Gdańsk   |          24 |                  4333.49 |  104004   |
| Lublin   |          23 |                  4236.69 |   97443.8 |
| Zamość   |          26 |                  3701.63 |   96242.3 |
| Poznań   |          28 |                  2954.46 |   82725   |
| Warszawa |          20 |                  3628.5  |   72570   |
| Kraków   |          22 |                  2711.38 |   59650.2 |

## Q5 [agregacja + collect, W3]

5 klientów o najwyższych wydatkach z listą kupowanych kategorii.

```cypher
MATCH (c:Customer)-[b:BOUGHT]->(p:Product)-[:BELONGS_TO]->(cat:Category)
RETURN c.customer_id AS id, c.name AS customer,
       round(sum(b.quantity * p.price), 2) AS spent,
       count(b) AS purchases,
       collect(DISTINCT cat.name) AS categories
ORDER BY spent DESC
LIMIT 5
```

| id   | customer         |   spent |   purchases | categories                                                          |
|:-----|:-----------------|--------:|------------:|:--------------------------------------------------------------------|
| K096 | Anna Dąbrowska   | 15955.8 |          10 | ['Elektronika', 'Książki', 'Sport', 'Moda', 'Zabawki', 'Spożywcze'] |
| K074 | Magda Zielińska  | 15139   |           9 | ['Elektronika', 'Książki', 'Sport']                                 |
| K122 | Michał Dąbrowski | 13496.9 |           7 | ['Elektronika', 'Sport']                                            |
| K089 | Julia Kowalska   | 12087.7 |           8 | ['Elektronika', 'Sport', 'Zabawki', 'Uroda']                        |
| K081 | Ilona Wójcik     | 11955   |          11 | ['Elektronika', 'Sport', 'Dom i ogród', 'Zabawki']                  |

## Q6 [wzorzec ścieżki, W2]

„Klienci, którzy kupili produkt P001, kupili również” – 5 produktów z największą liczbą wspólnych klientów.

```cypher
MATCH (:Product {product_id: "P001"})<-[:BOUGHT]-(c:Customer)-[:BOUGHT]->(other:Product)
WHERE other.product_id <> "P001"
RETURN other.product_id AS id, other.name AS product,
       count(DISTINCT c) AS common_customers
ORDER BY common_customers DESC, id
LIMIT 5
```

| id   | product               |   common_customers |
|:-----|:----------------------|-------------------:|
| P002 | Słuchawki Domeo Basic |                  2 |
| P020 | Klawiatura Fiora Max  |                  2 |
| P064 | Bidon Lumen Plus      |                  2 |
| P010 | Głośnik Sportaro Max  |                  1 |
| P012 | Głośnik Volta Basic   |                  1 |

## Q7 [wzorzec ścieżki (collaborative filtering), W2]

Rekomendacje dla klienta K072: produkty kupione przez klientów o podobnych zakupach, których K072 jeszcze nie ma.

```cypher
MATCH (me:Customer {customer_id: "K072"})-[:BOUGHT]->(p:Product)<-[:BOUGHT]-(peer:Customer)
WITH me, peer, count(DISTINCT p) AS similarity
MATCH (peer)-[b:BOUGHT]->(rec:Product)
WHERE NOT (me)-[:BOUGHT]->(rec) AND b.rating >= 4
MATCH (rec)-[:BELONGS_TO]->(cat:Category)
RETURN rec.product_id AS id, rec.name AS product, cat.name AS category,
       sum(similarity) AS score, count(DISTINCT peer) AS peers
ORDER BY score DESC, peers DESC
LIMIT 5
```

| id   | product            | category   |   score |   peers |
|:-----|:-------------------|:-----------|--------:|--------:|
| P117 | Suszarka Volta Max | Uroda      |      25 |      12 |
| P095 | Czapka Arctis Pro  | Moda       |      19 |       9 |
| P089 | Kurtka Domeo Basic | Moda       |      16 |       9 |
| P111 | Krem Kreda Basic   | Uroda      |      15 |       7 |
| P099 | Zegarek Arctis Max | Moda       |      13 |       7 |

## Q8 [shortestPath, W5]

Najkrótszy łańcuch obserwowania (FOLLOWS) od klienta K072 do klienta K031.

```cypher
MATCH path = shortestPath(
  (a:Customer {customer_id: "K072"})-[:FOLLOWS*..10]->(b:Customer {customer_id: "K031"}))
RETURN [n IN nodes(path) | n.customer_id + " " + n.name] AS chain,
       length(path) AS hops
```

| chain                                                                                                                                                                                                           |   hops |
|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------:|
| ['K072 Ola Zielińska', 'K110 Magda Kowalska', 'K190 Kasia Kozłowska', 'K037 Magda Dąbrowska', 'K085 Marek Kozłowski', 'K050 Bartek Wójcik', 'K169 Zofia Szymańska', 'K060 Anna Wójcik', 'K031 Magda Zielińska'] |      8 |

## Q9 [ścieżka o zmiennej długości, W5]

Zasięg wpływu: 5 klientów, do których najwięcej osób dociera w 1–3 krokach FOLLOWS (influencerzy).

```cypher
MATCH (influencer:Customer)<-[:FOLLOWS*1..3]-(fan:Customer)
WHERE fan <> influencer
RETURN influencer.customer_id AS id, influencer.name AS customer,
       count(DISTINCT fan) AS reach_3_hops
ORDER BY reach_3_hops DESC
LIMIT 5
```

| id   | customer           |   reach_3_hops |
|:-----|:-------------------|---------------:|
| K029 | Jakub Krawczyk     |             28 |
| K064 | Michał Kamiński    |             24 |
| K187 | Wiktoria Zielińska |             23 |
| K190 | Kasia Kozłowska    |             23 |
| K094 | Zofia Nowak        |             22 |

## Q10 [ścieżka o zmiennej długości, W2/W5]

Rekomendacje społeczne dla K072: produkty ocenione na 5 przez osoby obserwowane przez K072 w 1–2 krokach.

```cypher
MATCH (me:Customer {customer_id: "K072"})-[:FOLLOWS*1..2]->(friend:Customer)-[b:BOUGHT]->(p:Product)
WHERE b.rating = 5 AND NOT (me)-[:BOUGHT]->(p) AND friend <> me
RETURN p.product_id AS id, p.name AS product,
       collect(DISTINCT friend.name) AS recommended_by
ORDER BY size(recommended_by) DESC, id
LIMIT 5
```

| id   | product                 | recommended_by                          |
|:-----|:------------------------|:----------------------------------------|
| P043 | Komiks Zielono Max      | ['Kasia Kozłowska', 'Magda Wiśniewska'] |
| P003 | Słuchawki Zielono Plus  | ['Paweł Wiśniewski']                    |
| P012 | Głośnik Volta Basic     | ['Paweł Wiśniewski']                    |
| P036 | Biografia Bitwave Basic | ['Kasia Kozłowska']                     |
| P061 | Kask Fiora Max          | ['Kasia Kozłowska']                     |

## Q11 [agregacja (HAVING), W3]

Klienci kupujący w co najmniej 5 kategoriach (kandydaci do cross-sellingu).

```cypher
MATCH (c:Customer)-[:BOUGHT]->(:Product)-[:BELONGS_TO]->(cat:Category)
WITH c, count(DISTINCT cat) AS n_categories, collect(DISTINCT cat.name) AS categories
WHERE n_categories >= 5
RETURN c.customer_id AS id, c.name AS customer, n_categories, categories
ORDER BY n_categories DESC, id
```

| id   | customer          |   n_categories | categories                                                                   |
|:-----|:------------------|---------------:|:-----------------------------------------------------------------------------|
| K191 | Kamil Kowalski    |              7 | ['Książki', 'Sport', 'Dom i ogród', 'Moda', 'Zabawki', 'Uroda', 'Spożywcze'] |
| K026 | Ilona Szymańska   |              6 | ['Elektronika', 'Sport', 'Dom i ogród', 'Moda', 'Uroda', 'Spożywcze']        |
| K096 | Anna Dąbrowska    |              6 | ['Elektronika', 'Książki', 'Sport', 'Moda', 'Zabawki', 'Spożywcze']          |
| K196 | Szymon Zieliński  |              6 | ['Książki', 'Sport', 'Dom i ogród', 'Moda', 'Zabawki', 'Uroda']              |
| K004 | Michał Zieliński  |              5 | ['Elektronika', 'Książki', 'Dom i ogród', 'Moda', 'Zabawki']                 |
| K011 | Julia Kamińska    |              5 | ['Elektronika', 'Książki', 'Sport', 'Moda', 'Uroda']                         |
| K020 | Marek Woźniak     |              5 | ['Książki', 'Sport', 'Moda', 'Uroda', 'Spożywcze']                           |
| K024 | Marek Kamiński    |              5 | ['Elektronika', 'Książki', 'Sport', 'Zabawki', 'Spożywcze']                  |
| K053 | Natalia Dąbrowska |              5 | ['Elektronika', 'Książki', 'Sport', 'Dom i ogród', 'Spożywcze']              |
| K061 | Szymon Wiśniewski |              5 | ['Elektronika', 'Książki', 'Dom i ogród', 'Uroda', 'Spożywcze']              |
| K069 | Paweł Kowalski    |              5 | ['Książki', 'Sport', 'Dom i ogród', 'Uroda', 'Spożywcze']                    |
| K079 | Ewa Lewandowska   |              5 | ['Książki', 'Sport', 'Dom i ogród', 'Moda', 'Zabawki']                       |
| K080 | Zofia Dąbrowska   |              5 | ['Elektronika', 'Sport', 'Moda', 'Zabawki', 'Spożywcze']                     |
| K082 | Bartek Woźniak    |              5 | ['Książki', 'Sport', 'Dom i ogród', 'Uroda', 'Spożywcze']                    |
| K085 | Marek Kozłowski   |              5 | ['Elektronika', 'Książki', 'Sport', 'Zabawki', 'Uroda']                      |
| K125 | Julia Zielińska   |              5 | ['Elektronika', 'Książki', 'Sport', 'Moda', 'Zabawki']                       |
| K140 | Kasia Kamińska    |              5 | ['Elektronika', 'Książki', 'Sport', 'Moda', 'Spożywcze']                     |
| K148 | Natalia Kozłowska |              5 | ['Książki', 'Sport', 'Dom i ogród', 'Uroda', 'Spożywcze']                    |
| K166 | Zofia Kozłowska   |              5 | ['Książki', 'Dom i ogród', 'Moda', 'Uroda', 'Spożywcze']                     |
| K170 | Bartek Kowalski   |              5 | ['Sport', 'Dom i ogród', 'Moda', 'Uroda', 'Spożywcze']                       |
| K189 | Szymon Woźniak    |              5 | ['Książki', 'Sport', 'Dom i ogród', 'Moda', 'Zabawki']                       |
| K190 | Kasia Kozłowska   |              5 | ['Książki', 'Sport', 'Moda', 'Zabawki', 'Uroda']                             |

## Q12 [agregacja, W6]

Kwartalna liczba transakcji i przychód (trend sprzedaży).

```cypher
MATCH (:Customer)-[b:BOUGHT]->(p:Product)
WITH b.date.year AS year, b.date.quarter AS quarter, b, p
RETURN year, quarter, count(b) AS transactions,
       round(sum(b.quantity * p.price), 2) AS revenue
ORDER BY year, quarter
```

|   year |   quarter |   transactions |   revenue |
|-------:|----------:|---------------:|----------:|
|   2025 |         1 |            155 |  104643   |
|   2025 |         2 |            152 |  106101   |
|   2025 |         3 |            158 |   98788.5 |
|   2025 |         4 |            152 |   85737.5 |
|   2026 |         1 |            176 |  104257   |
|   2026 |         2 |            161 |   91009.6 |
|   2026 |         3 |            168 |  101580   |
|   2026 |         4 |            111 |   55419.6 |

## Q13 [wyszukujące (OPTIONAL MATCH), W1]

Produkty o najsłabszej sprzedaży – kupione przez mniej niż 4 klientów (kandydaci do przeceny lub wycofania).

```cypher
MATCH (p:Product)-[:BELONGS_TO]->(cat:Category)
OPTIONAL MATCH (c:Customer)-[:BOUGHT]->(p)
WITH p, cat, count(c) AS buyers
WHERE buyers < 4
RETURN p.product_id AS id, p.name AS product, cat.name AS category,
       p.price AS price, buyers
ORDER BY buyers, category
```

| id   | product                   | category    |   price |   buyers |
|:-----|:--------------------------|:------------|--------:|---------:|
| P050 | Mata do jogi Bitwave Plus | Sport       | 2383.96 |        2 |
| P017 | Router Lumen Basic        | Elektronika |  770.69 |        3 |
| P007 | Powerbank Domeo Plus      | Elektronika |  944.02 |        3 |
| P052 | Rower Nordix Max          | Sport       |  301.76 |        3 |
