# Wyniki zapytań – graf penguins


## Instrukcja – Ćwiczenie 2: pierwsze kroki w Cypher

### I2.0 – Czyszczenie grafu przed startem

```cypher
MATCH (n) DETACH DELETE n
```

_(brak wierszy – zapytanie modyfikujące)_

### I2.2 – Utworzenie węzła Penguin

```cypher
CREATE (p:Penguin {body_mass_g: 3900, sex: "female", note: "węzeł testowy"}) RETURN p
```

Zmiany: `{'labels_added': 1, 'nodes_created': 1, 'properties_set': 3}`

| p                                                               |
|:----------------------------------------------------------------|
| {'note': 'węzeł testowy', 'body_mass_g': 3900, 'sex': 'female'} |

### I2.3 – Utworzenie węzła Island

```cypher
CREATE (i:Island {name: "Testowa"}) RETURN i
```

Zmiany: `{'labels_added': 1, 'nodes_created': 1, 'properties_set': 1}`

| i                   |
|:--------------------|
| {'name': 'Testowa'} |

### I2.4 – Relacja LIVES_ON

```cypher
MATCH (p:Penguin {note: "węzeł testowy"}),
      (i:Island {name: "Testowa"})
CREATE (p)-[:LIVES_ON]->(i)
```

Zmiany: `{'relationships_created': 1}`

_(brak wierszy – zapytanie modyfikujące)_

### I2.5 – Wyświetlenie fragmentu grafu

```cypher
MATCH (p:Penguin)-[r:LIVES_ON]->(i:Island)
RETURN p, type(r) AS r, i
```

| p                                                               | r        | i                   |
|:----------------------------------------------------------------|:---------|:--------------------|
| {'note': 'węzeł testowy', 'body_mass_g': 3900, 'sex': 'female'} | LIVES_ON | {'name': 'Testowa'} |

### I2.6 – Modyfikacja SET

```cypher
MATCH (p:Penguin {note: "węzeł testowy"})
SET p.verified = true, p.body_mass_g = 3950
RETURN p
```

Zmiany: `{'properties_set': 2}`

| p                                                                                 |
|:----------------------------------------------------------------------------------|
| {'note': 'węzeł testowy', 'body_mass_g': 3950, 'sex': 'female', 'verified': True} |

### I2.6b – Usunięcie właściwości REMOVE

```cypher
MATCH (p:Penguin {note: "węzeł testowy"})
REMOVE p.verified
RETURN p
```

Zmiany: `{'properties_set': 1}`

| p                                                               |
|:----------------------------------------------------------------|
| {'note': 'węzeł testowy', 'body_mass_g': 3950, 'sex': 'female'} |

### I2.7 – DETACH DELETE pingwina

```cypher
MATCH (p:Penguin {note: "węzeł testowy"})
DETACH DELETE p
```

Zmiany: `{'nodes_deleted': 1, 'relationships_deleted': 1}`

_(brak wierszy – zapytanie modyfikujące)_

### I2.7b – DELETE wyspy

```cypher
MATCH (i:Island {name: "Testowa"}) DELETE i
```

Zmiany: `{'nodes_deleted': 1}`

_(brak wierszy – zapytanie modyfikujące)_

### I2.8 – Graf pusty

```cypher
MATCH (n) RETURN count(n) AS n
```

|   n |
|----:|
|   0 |


## Instrukcja – Ćwiczenie 3: model grafu i import LOAD CSV

### I3.1a – Ograniczenie unikatowości Species

```cypher
CREATE CONSTRAINT species_name IF NOT EXISTS FOR (s:Species) REQUIRE s.name IS UNIQUE
```

Zmiany: `{'constraints_added': 1}`

_(brak wierszy – zapytanie modyfikujące)_

### I3.1b – Ograniczenie unikatowości Island

```cypher
CREATE CONSTRAINT island_name IF NOT EXISTS FOR (i:Island) REQUIRE i.name IS UNIQUE
```

Zmiany: `{'constraints_added': 1}`

_(brak wierszy – zapytanie modyfikujące)_

### I3.2 – Import LOAD CSV

```cypher
LOAD CSV WITH HEADERS FROM "file:///penguins.csv" AS row
MERGE (s:Species {name: row.species})
MERGE (i:Island {name: row.island})
CREATE (p:Penguin {
  bill_length_mm: toFloat(row.bill_length_mm),
  bill_depth_mm: toFloat(row.bill_depth_mm),
  flipper_length_mm: toInteger(row.flipper_length_mm),
  body_mass_g: toInteger(row.body_mass_g),
  sex: CASE row.sex WHEN "" THEN null ELSE row.sex END,
  year: toInteger(row.year)
})
CREATE (p)-[:OF_SPECIES]->(s)
CREATE (p)-[:LIVES_ON]->(i)
```

Zmiany: `{'labels_added': 350, 'relationships_created': 688, 'nodes_created': 350, 'properties_set': 2051}`

_(brak wierszy – zapytanie modyfikujące)_

### I3.3a – Liczba pingwinów

```cypher
MATCH (p:Penguin) RETURN count(p) AS cnt
```

|   cnt |
|------:|
|   344 |

### I3.3b – Gatunki

```cypher
MATCH (s:Species) RETURN s.name AS name ORDER BY s.name
```

| name      |
|:----------|
| Adelie    |
| Chinstrap |
| Gentoo    |

### I3.3c – Relacje wg typu

```cypher
MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS cnt
```

| type       |   cnt |
|:-----------|------:|
| OF_SPECIES |   344 |
| LIVES_ON   |   344 |

### I3.4 – Fragment grafu (liczba ścieżek, w Browserze widok Graph)

```cypher
MATCH path = (p:Penguin)-[:OF_SPECIES|LIVES_ON]->()
RETURN count(path) AS paths
```

|   paths |
|--------:|
|     688 |


## Instrukcja – Ćwiczenie 4: zapytania wyszukujące

### I4.1 – Pingwiny Adelie

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(:Species {name: "Adelie"})
RETURN count(p) AS cnt
```

|   cnt |
|------:|
|   152 |

### I4.2 – Masa > 4500

```cypher
MATCH (p:Penguin) WHERE p.body_mass_g > 4500 RETURN count(p) AS cnt
```

|   cnt |
|------:|
|   115 |

### I4.3 – Samice Gentoo

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE s.name = "Gentoo" AND p.sex = "female"
RETURN count(p) AS cnt
```

|   cnt |
|------:|
|    58 |

### I4.4a – Wyspy Dream/Torgersen

```cypher
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE i.name IN ["Dream", "Torgersen"]
RETURN count(p) AS cnt
```

|   cnt |
|------:|
|   176 |

### I4.4b – Gatunki Adelie/Chinstrap

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE s.name IN ["Adelie", "Chinstrap"]
RETURN count(p) AS cnt
```

|   cnt |
|------:|
|   220 |

### I4.5 – 5 najcięższych

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species),
      (p)-[:LIVES_ON]->(i:Island)
WHERE p.body_mass_g IS NOT NULL
RETURN s.name AS species, i.name AS island,
       p.sex AS sex, p.body_mass_g AS mass
ORDER BY mass DESC
LIMIT 5
```

| species   | island   | sex   |   mass |
|:----------|:---------|:------|-------:|
| Gentoo    | Biscoe   | male  |   6300 |
| Gentoo    | Biscoe   | male  |   6050 |
| Gentoo    | Biscoe   | male  |   6000 |
| Gentoo    | Biscoe   | male  |   6000 |
| Gentoo    | Biscoe   | male  |   5950 |

### I4.5b – To samo BEZ filtra IS NOT NULL (null na początku)

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species),
      (p)-[:LIVES_ON]->(i:Island)
RETURN s.name AS species, i.name AS island,
       p.sex AS sex, p.body_mass_g AS mass
ORDER BY mass DESC
LIMIT 5
```

| species   | island    | sex   |   mass |
|:----------|:----------|:------|-------:|
| Adelie    | Torgersen | nan   |    nan |
| Gentoo    | Biscoe    | nan   |    nan |
| Gentoo    | Biscoe    | male  |   6300 |
| Gentoo    | Biscoe    | male  |   6050 |
| Gentoo    | Biscoe    | male  |   6000 |

### I4.6 – Brak płci

```cypher
MATCH (p:Penguin) WHERE p.sex IS NULL RETURN count(p) AS cnt
```

|   cnt |
|------:|
|    11 |

### I4.7 – Unikatowe wyspy

```cypher
MATCH (:Penguin)-[:LIVES_ON]->(i:Island)
RETURN DISTINCT i.name AS island
```

| island    |
|:----------|
| Torgersen |
| Biscoe    |
| Dream     |


## Instrukcja – Ćwiczenie 5: zapytania agregacyjne

### I5.1 – Średnia masa wg gatunku

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
RETURN s.name AS species,
       round(avg(p.body_mass_g), 2) AS avg_mass,
       count(p) AS cnt
ORDER BY avg_mass DESC
```

| species   |   avg_mass |   cnt |
|:----------|-----------:|------:|
| Gentoo    |    5076.02 |   124 |
| Chinstrap |    3733.09 |    68 |
| Adelie    |    3700.66 |   152 |

### I5.2 – Średnia masa samic wg gatunku

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE p.sex = "female"
RETURN s.name AS species,
       round(avg(p.body_mass_g), 2) AS avg_mass,
       count(p) AS cnt
ORDER BY avg_mass DESC
```

| species   |   avg_mass |   cnt |
|:----------|-----------:|------:|
| Gentoo    |    4679.74 |    58 |
| Chinstrap |    3527.21 |    34 |
| Adelie    |    3368.84 |    73 |

### I5.3 – Pary gatunek-wyspa

```cypher
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)
      -[:LIVES_ON]->(i:Island)
RETURN s.name AS species, i.name AS island,
       count(p) AS cnt
ORDER BY cnt DESC
```

| species   | island    |   cnt |
|:----------|:----------|------:|
| Gentoo    | Biscoe    |   124 |
| Chinstrap | Dream     |    68 |
| Adelie    | Dream     |    56 |
| Adelie    | Torgersen |    52 |
| Adelie    | Biscoe    |    44 |

### I5.4 – HAVING: wyspy > 100

```cypher
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
WITH i.name AS island, count(p) AS cnt
WHERE cnt > 100
RETURN island, cnt
ORDER BY cnt DESC
```

| island   |   cnt |
|:---------|------:|
| Biscoe   |   168 |
| Dream    |   124 |

### I5.5 – collect: gatunki na wyspach

```cypher
MATCH (s:Species)<-[:OF_SPECIES]-(:Penguin)
      -[:LIVES_ON]->(i:Island)
RETURN i.name AS island,
       collect(DISTINCT s.name) AS species
```

| island    | species                 |
|:----------|:------------------------|
| Torgersen | ['Adelie']              |
| Biscoe    | ['Gentoo', 'Adelie']    |
| Dream     | ['Adelie', 'Chinstrap'] |


## Instrukcja – Ćwiczenie 6: wzorce ścieżek

### I6.1 – Gatunki dzielące wyspę z Adelie

```cypher
MATCH (:Species {name: "Adelie"})<-[:OF_SPECIES]-(:Penguin)
      -[:LIVES_ON]->(i:Island)<-[:LIVES_ON]-(:Penguin)
      -[:OF_SPECIES]->(s2:Species)
WHERE s2.name <> "Adelie"
RETURN DISTINCT i.name AS island, s2.name AS species
```

| island   | species   |
|:---------|:----------|
| Dream    | Chinstrap |
| Biscoe   | Gentoo    |

### I6.2 – Wyspy z > 1 gatunkiem

```cypher
MATCH (s:Species)<-[:OF_SPECIES]-(:Penguin)
      -[:LIVES_ON]->(i:Island)
WITH i.name AS island,
     collect(DISTINCT s.name) AS species
WHERE size(species) > 1
RETURN island, species
```

| island   | species                 |
|:---------|:------------------------|
| Biscoe   | ['Gentoo', 'Adelie']    |
| Dream    | ['Adelie', 'Chinstrap'] |


## Ćwiczenie samodzielne nr 1: zapytania wyszukujące

### S1.1 – Chinstrap z Dream, masa > 3500 g – lista

```cypher
MATCH (s:Species {name: "Chinstrap"})<-[:OF_SPECIES]-(p:Penguin)
      -[:LIVES_ON]->(i:Island {name: "Dream"})
WHERE p.body_mass_g > 3500
RETURN p.sex AS sex, p.bill_length_mm AS bill_length_mm,
       p.flipper_length_mm AS flipper_length_mm,
       p.body_mass_g AS body_mass_g, p.year AS year
ORDER BY body_mass_g DESC
```

| sex    |   bill_length_mm |   flipper_length_mm |   body_mass_g |   year |
|:-------|-----------------:|--------------------:|--------------:|-------:|
| male   |             52   |                 210 |          4800 |   2008 |
| male   |             52.8 |                 205 |          4550 |   2008 |
| male   |             53.5 |                 205 |          4500 |   2008 |
| male   |             50.8 |                 201 |          4450 |   2009 |
| male   |             49.2 |                 195 |          4400 |   2007 |
| male   |             49   |                 212 |          4300 |   2009 |
| male   |             54.2 |                 201 |          4300 |   2008 |
| male   |             52   |                 197 |          4150 |   2007 |
| female |             46   |                 195 |          4150 |   2007 |
| male   |             50.8 |                 210 |          4100 |   2009 |
| male   |             51   |                 203 |          4100 |   2008 |
| male   |             49.3 |                 203 |          4050 |   2009 |
| male   |             52   |                 201 |          4050 |   2007 |
| male   |             50.5 |                 201 |          4050 |   2007 |
| male   |             50.7 |                 203 |          4050 |   2009 |
| male   |             55.8 |                 207 |          4000 |   2009 |
| male   |             51.4 |                 201 |          3950 |   2009 |
| male   |             49   |                 210 |          3950 |   2008 |
| male   |             51.9 |                 206 |          3950 |   2009 |
| female |             45.2 |                 198 |          3950 |   2007 |
| male   |             50   |                 196 |          3900 |   2007 |
| female |             47.5 |                 199 |          3900 |   2008 |
| female |             47.6 |                 195 |          3850 |   2008 |
| male   |             49.5 |                 200 |          3800 |   2008 |
| male   |             50.2 |                 202 |          3800 |   2009 |
| female |             46.6 |                 193 |          3800 |   2007 |
| male   |             50.6 |                 193 |          3800 |   2007 |
| male   |             51.7 |                 194 |          3775 |   2007 |
| male   |             49.6 |                 193 |          3775 |   2009 |
| female |             50.2 |                 198 |          3775 |   2009 |
| male   |             51.3 |                 197 |          3750 |   2007 |
| male   |             52.7 |                 197 |          3725 |   2007 |
| female |             58   |                 181 |          3700 |   2007 |
| female |             47   |                 185 |          3700 |   2007 |
| female |             46.4 |                 191 |          3700 |   2008 |
| male   |             51.3 |                 198 |          3700 |   2007 |
| female |             50.9 |                 196 |          3675 |   2009 |
| female |             49.8 |                 198 |          3675 |   2009 |
| female |             46.8 |                 189 |          3650 |   2009 |
| female |             45.7 |                 195 |          3650 |   2009 |
| female |             46.2 |                 187 |          3650 |   2008 |
| male   |             51.3 |                 193 |          3650 |   2007 |
| female |             42.4 |                 181 |          3600 |   2007 |
| male   |             49.7 |                 195 |          3600 |   2008 |
| female |             45.7 |                 193 |          3600 |   2009 |
| female |             45.9 |                 190 |          3575 |   2007 |
| male   |             50.9 |                 196 |          3550 |   2008 |
| female |             45.6 |                 194 |          3525 |   2009 |
| female |             45.4 |                 188 |          3525 |   2007 |

### S1.1b – Chinstrap z Dream, masa > 3500 g – liczba

```cypher
MATCH (:Species {name: "Chinstrap"})<-[:OF_SPECIES]-(p:Penguin)
      -[:LIVES_ON]->(:Island {name: "Dream"})
WHERE p.body_mass_g > 3500
RETURN count(p) AS cnt
```

|   cnt |
|------:|
|    49 |

### S1.2 – 10 pingwinów o najdłuższym dziobie

```cypher
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.bill_length_mm IS NOT NULL
RETURN s.name AS species, i.name AS island,
       p.bill_length_mm AS bill_length_mm
ORDER BY bill_length_mm DESC
LIMIT 10
```

| species   | island   |   bill_length_mm |
|:----------|:---------|-----------------:|
| Gentoo    | Biscoe   |             59.6 |
| Chinstrap | Dream    |             58   |
| Gentoo    | Biscoe   |             55.9 |
| Chinstrap | Dream    |             55.8 |
| Gentoo    | Biscoe   |             55.1 |
| Gentoo    | Biscoe   |             54.3 |
| Chinstrap | Dream    |             54.2 |
| Chinstrap | Dream    |             53.5 |
| Gentoo    | Biscoe   |             53.4 |
| Chinstrap | Dream    |             52.8 |

### S1.3 – Rok 2007, Torgersen lub Biscoe – lista

```cypher
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.year = 2007 AND i.name IN ["Torgersen", "Biscoe"]
RETURN i.name AS island, s.name AS species, p.sex AS sex,
       p.body_mass_g AS body_mass_g
ORDER BY island, species
```

| island    | species   | sex    |   body_mass_g |
|:----------|:----------|:-------|--------------:|
| Biscoe    | Adelie    | female |          3150 |
| Biscoe    | Adelie    | male   |          3550 |
| Biscoe    | Adelie    | female |          3800 |
| Biscoe    | Adelie    | female |          3800 |
| Biscoe    | Adelie    | male   |          3950 |
| Biscoe    | Adelie    | female |          3200 |
| Biscoe    | Adelie    | male   |          3800 |
| Biscoe    | Adelie    | male   |          3950 |
| Biscoe    | Adelie    | male   |          3600 |
| Biscoe    | Adelie    | female |          3400 |
| Biscoe    | Gentoo    | male   |          5700 |
| Biscoe    | Gentoo    | female |          4800 |
| Biscoe    | Gentoo    | female |          4400 |
| Biscoe    | Gentoo    | male   |          5550 |
| Biscoe    | Gentoo    | female |          4800 |
| Biscoe    | Gentoo    | male   |          5350 |
| Biscoe    | Gentoo    | male   |          5050 |
| Biscoe    | Gentoo    | female |          4650 |
| Biscoe    | Gentoo    | male   |          5650 |
| Biscoe    | Gentoo    | female |          4400 |
| Biscoe    | Gentoo    | female |          5000 |
| Biscoe    | Gentoo    | female |          4600 |
| Biscoe    | Gentoo    | male   |          5150 |
| Biscoe    | Gentoo    | male   |          6050 |
| Biscoe    | Gentoo    | male   |          5850 |
| Biscoe    | Gentoo    | male   |          6300 |
| Biscoe    | Gentoo    | male   |          5550 |
| Biscoe    | Gentoo    | female |          4700 |
| Biscoe    | Gentoo    | male   |          5700 |
| Biscoe    | Gentoo    | male   |          5250 |
| Biscoe    | Gentoo    | nan    |          4100 |
| Biscoe    | Gentoo    | male   |          5200 |
| Biscoe    | Gentoo    | female |          4200 |
| Biscoe    | Gentoo    | female |          4500 |
| Biscoe    | Gentoo    | male   |          5100 |
| Biscoe    | Gentoo    | female |          4650 |
| Biscoe    | Gentoo    | female |          5050 |
| Biscoe    | Gentoo    | female |          5000 |
| Biscoe    | Gentoo    | female |          4450 |
| Biscoe    | Gentoo    | male   |          5850 |
| Biscoe    | Gentoo    | female |          4550 |
| Biscoe    | Gentoo    | male   |          5700 |
| Biscoe    | Gentoo    | female |          4150 |
| Biscoe    | Gentoo    | male   |          5400 |
| Torgersen | Adelie    | male   |          3750 |
| Torgersen | Adelie    | female |          3800 |
| Torgersen | Adelie    | female |          3250 |
| Torgersen | Adelie    | nan    |           nan |
| Torgersen | Adelie    | female |          3450 |
| Torgersen | Adelie    | male   |          3650 |
| Torgersen | Adelie    | female |          3625 |
| Torgersen | Adelie    | male   |          4675 |
| Torgersen | Adelie    | nan    |          3475 |
| Torgersen | Adelie    | nan    |          4250 |
| Torgersen | Adelie    | nan    |          3300 |
| Torgersen | Adelie    | nan    |          3700 |
| Torgersen | Adelie    | female |          3200 |
| Torgersen | Adelie    | male   |          3800 |
| Torgersen | Adelie    | male   |          4400 |
| Torgersen | Adelie    | male   |          4200 |

_… pokazano 60 z 64 wierszy_

### S1.3b – Rok 2007, Torgersen lub Biscoe – liczba (z podziałem)

```cypher
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.year = 2007 AND i.name IN ["Torgersen", "Biscoe"]
RETURN i.name AS island, count(p) AS cnt
ORDER BY island
```

| island    |   cnt |
|:----------|------:|
| Biscoe    |    44 |
| Torgersen |    20 |

### S1.3c – Rok 2007, Torgersen lub Biscoe – liczba łączna

```cypher
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.year = 2007 AND i.name IN ["Torgersen", "Biscoe"]
RETURN count(p) AS cnt
```

|   cnt |
|------:|
|    64 |

### S1.4 – Pingwiny bez informacji o płci

```cypher
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.sex IS NULL
RETURN s.name AS species, i.name AS island, p.year AS year,
       p.body_mass_g AS body_mass_g, p.bill_length_mm AS bill_length_mm
ORDER BY species, island
```

| species   | island    |   year |   body_mass_g |   bill_length_mm |
|:----------|:----------|-------:|--------------:|-----------------:|
| Adelie    | Dream     |   2007 |          2975 |             37.5 |
| Adelie    | Torgersen |   2007 |           nan |            nan   |
| Adelie    | Torgersen |   2007 |          3475 |             34.1 |
| Adelie    | Torgersen |   2007 |          4250 |             42   |
| Adelie    | Torgersen |   2007 |          3300 |             37.8 |
| Adelie    | Torgersen |   2007 |          3700 |             37.8 |
| Gentoo    | Biscoe    |   2009 |           nan |            nan   |
| Gentoo    | Biscoe    |   2009 |          4725 |             47.3 |
| Gentoo    | Biscoe    |   2008 |          4650 |             46.2 |
| Gentoo    | Biscoe    |   2007 |          4100 |             44.5 |
| Gentoo    | Biscoe    |   2009 |          4875 |             44.5 |

### S1.4b – Braki płci wg gatunku i wyspy

```cypher
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.sex IS NULL
RETURN s.name AS species, i.name AS island, count(p) AS missing_sex
ORDER BY missing_sex DESC
```

| species   | island    |   missing_sex |
|:----------|:----------|--------------:|
| Adelie    | Torgersen |             5 |
| Gentoo    | Biscoe    |             5 |
| Adelie    | Dream     |             1 |

### S1.5 – Masa 3000–3500 g włącznie

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE 3000 <= p.body_mass_g <= 3500
RETURN s.name AS species, p.sex AS sex, p.body_mass_g AS body_mass_g
ORDER BY body_mass_g ASC
```

| species   | sex    |   body_mass_g |
|:----------|:-------|--------------:|
| Adelie    | female |          3000 |
| Adelie    | female |          3000 |
| Adelie    | female |          3050 |
| Adelie    | female |          3050 |
| Adelie    | female |          3050 |
| Adelie    | female |          3050 |
| Adelie    | female |          3075 |
| Adelie    | female |          3100 |
| Adelie    | female |          3150 |
| Adelie    | female |          3150 |
| Adelie    | female |          3150 |
| Adelie    | female |          3150 |
| Adelie    | female |          3175 |
| Adelie    | female |          3175 |
| Adelie    | female |          3200 |
| Adelie    | female |          3200 |
| Adelie    | female |          3200 |
| Adelie    | female |          3200 |
| Chinstrap | female |          3200 |
| Adelie    | female |          3250 |
| Adelie    | female |          3250 |
| Chinstrap | male   |          3250 |
| Chinstrap | female |          3250 |
| Chinstrap | female |          3250 |
| Adelie    | female |          3275 |
| Adelie    | female |          3300 |
| Adelie    | female |          3300 |
| Adelie    | nan    |          3300 |
| Adelie    | female |          3300 |
| Chinstrap | female |          3300 |
| Chinstrap | male   |          3300 |
| Adelie    | female |          3325 |
| Adelie    | female |          3325 |
| Adelie    | male   |          3325 |
| Adelie    | female |          3325 |
| Chinstrap | female |          3325 |
| Adelie    | female |          3350 |
| Adelie    | female |          3350 |
| Adelie    | female |          3350 |
| Chinstrap | female |          3350 |
| Chinstrap | female |          3350 |
| Adelie    | female |          3400 |
| Adelie    | female |          3400 |
| Adelie    | female |          3400 |
| Adelie    | female |          3400 |
| Chinstrap | female |          3400 |
| Chinstrap | female |          3400 |
| Chinstrap | male   |          3400 |
| Chinstrap | female |          3400 |
| Adelie    | female |          3425 |
| Adelie    | male   |          3425 |
| Adelie    | female |          3450 |
| Adelie    | female |          3450 |
| Adelie    | female |          3450 |
| Adelie    | female |          3450 |
| Adelie    | female |          3450 |
| Adelie    | female |          3450 |
| Chinstrap | female |          3450 |
| Chinstrap | male   |          3450 |
| Adelie    | male   |          3475 |

_… pokazano 60 z 69 wierszy_

### S1.5b – Masa 3000–3500 g – liczba

```cypher
MATCH (p:Penguin)
WHERE p.body_mass_g >= 3000 AND p.body_mass_g <= 3500
RETURN count(p) AS cnt
```

|   cnt |
|------:|
|    69 |


## Ćwiczenie samodzielne nr 2: agregacje i wzorce ścieżek

### S2.1 – Liczba pingwinów na wyspach

```cypher
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
RETURN i.name AS island, count(p) AS cnt
ORDER BY cnt DESC
```

| island    |   cnt |
|:----------|------:|
| Biscoe    |   168 |
| Dream     |   124 |
| Torgersen |    52 |

### S2.2 – Płetwa wg gatunku i płci

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE p.sex IS NOT NULL
RETURN s.name AS species, p.sex AS sex,
       round(avg(p.flipper_length_mm), 2) AS avg_flipper,
       min(p.flipper_length_mm) AS min_flipper,
       max(p.flipper_length_mm) AS max_flipper,
       count(p) AS cnt
ORDER BY species, sex
```

| species   | sex    |   avg_flipper |   min_flipper |   max_flipper |   cnt |
|:----------|:-------|--------------:|--------------:|--------------:|------:|
| Adelie    | female |        187.79 |           172 |           202 |    73 |
| Adelie    | male   |        192.41 |           178 |           210 |    73 |
| Chinstrap | female |        191.74 |           178 |           202 |    34 |
| Chinstrap | male   |        199.91 |           187 |           212 |    34 |
| Gentoo    | female |        212.71 |           203 |           222 |    58 |
| Gentoo    | male   |        221.54 |           208 |           231 |    61 |

### S2.3 – Średnia masa wg roku

```cypher
MATCH (p:Penguin)
RETURN p.year AS year,
       round(avg(p.body_mass_g), 2) AS avg_mass,
       count(p.body_mass_g) AS measured, count(p) AS cnt
ORDER BY year
```

|   year |   avg_mass |   measured |   cnt |
|-------:|-----------:|-----------:|------:|
|   2007 |    4124.54 |        109 |   110 |
|   2008 |    4266.67 |        114 |   114 |
|   2009 |    4210.29 |        119 |   120 |

### S2.3b – Średnia masa wg roku i gatunku (kontrola trendu)

```cypher
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
RETURN s.name AS species, p.year AS year,
       round(avg(p.body_mass_g), 2) AS avg_mass, count(p) AS cnt
ORDER BY species, year
```

| species   |   year |   avg_mass |   cnt |
|:----------|-------:|-----------:|------:|
| Adelie    |   2007 |    3696.43 |    50 |
| Adelie    |   2008 |    3742    |    50 |
| Adelie    |   2009 |    3664.9  |    52 |
| Chinstrap |   2007 |    3694.23 |    26 |
| Chinstrap |   2008 |    3800    |    18 |
| Chinstrap |   2009 |    3725    |    24 |
| Gentoo    |   2007 |    5070.59 |    34 |
| Gentoo    |   2008 |    5019.57 |    46 |
| Gentoo    |   2009 |    5140.7  |    44 |

### S2.4 – Wyspy z > 50 pingwinami Adelie (WITH … WHERE)

```cypher
MATCH (:Species {name: "Adelie"})<-[:OF_SPECIES]-(p:Penguin)
      -[:LIVES_ON]->(i:Island)
WITH i.name AS island, count(p) AS adelie_cnt
WHERE adelie_cnt > 50
RETURN island, adelie_cnt
ORDER BY adelie_cnt DESC
```

| island    |   adelie_cnt |
|:----------|-------------:|
| Dream     |           56 |
| Torgersen |           52 |

### S2.5a – Lista wysp dla każdego gatunku (collect)

```cypher
MATCH (s:Species)<-[:OF_SPECIES]-(:Penguin)-[:LIVES_ON]->(i:Island)
RETURN s.name AS species, collect(DISTINCT i.name) AS islands
ORDER BY species
```

| species   | islands                          |
|:----------|:---------------------------------|
| Adelie    | ['Dream', 'Biscoe', 'Torgersen'] |
| Chinstrap | ['Dream']                        |
| Gentoo    | ['Biscoe']                       |

### S2.5b – Gatunki występujące na tej samej wyspie co Gentoo (wzorzec ścieżki)

```cypher
MATCH (:Species {name: "Gentoo"})<-[:OF_SPECIES]-(:Penguin)
      -[:LIVES_ON]->(i:Island)<-[:LIVES_ON]-(:Penguin)
      -[:OF_SPECIES]->(s2:Species)
WHERE s2.name <> "Gentoo"
RETURN DISTINCT i.name AS island, s2.name AS species
```

| island   | species   |
|:---------|:----------|
| Biscoe   | Adelie    |
