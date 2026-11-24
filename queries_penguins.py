"""Laboratorium nr 5 – wszystkie zapytania Cypher na grafie penguins.

Skrypt wykonuje kolejno ćwiczenia z części instrukcyjnej (2-6) oraz ćwiczenia
samodzielne nr 1 i 2, a wyniki zapisuje do pliku wyniki_penguins.md.
Uruchomienie:  uv run queries_penguins.py
"""
from neo4j import GraphDatabase, Result
import pandas as pd

URI = "bolt://localhost:7687"

# (sekcja, identyfikator, opis, zapytanie)
Q = []


def q(section, qid, desc, cypher):
    Q.append((section, qid, desc, cypher.strip()))


# ---------------------------------------------------------------- Ćw. 2 (instrukcja)
S = "Instrukcja – Ćwiczenie 2: pierwsze kroki w Cypher"
q(S, "I2.0", "Czyszczenie grafu przed startem", "MATCH (n) DETACH DELETE n")
q(S, "I2.2", "Utworzenie węzła Penguin",
  'CREATE (p:Penguin {body_mass_g: 3900, sex: "female", note: "węzeł testowy"}) RETURN p')
q(S, "I2.3", "Utworzenie węzła Island", 'CREATE (i:Island {name: "Testowa"}) RETURN i')
q(S, "I2.4", "Relacja LIVES_ON", '''
MATCH (p:Penguin {note: "węzeł testowy"}),
      (i:Island {name: "Testowa"})
CREATE (p)-[:LIVES_ON]->(i)''')
q(S, "I2.5", "Wyświetlenie fragmentu grafu", '''
MATCH (p:Penguin)-[r:LIVES_ON]->(i:Island)
RETURN p, type(r) AS r, i''')
q(S, "I2.6", "Modyfikacja SET", '''
MATCH (p:Penguin {note: "węzeł testowy"})
SET p.verified = true, p.body_mass_g = 3950
RETURN p''')
q(S, "I2.6b", "Usunięcie właściwości REMOVE", '''
MATCH (p:Penguin {note: "węzeł testowy"})
REMOVE p.verified
RETURN p''')
q(S, "I2.7", "DETACH DELETE pingwina", '''
MATCH (p:Penguin {note: "węzeł testowy"})
DETACH DELETE p''')
q(S, "I2.7b", "DELETE wyspy", 'MATCH (i:Island {name: "Testowa"}) DELETE i')
q(S, "I2.8", "Graf pusty", "MATCH (n) RETURN count(n) AS n")

# ---------------------------------------------------------------- Ćw. 3 (instrukcja)
S = "Instrukcja – Ćwiczenie 3: model grafu i import LOAD CSV"
q(S, "I3.1a", "Ograniczenie unikatowości Species",
  "CREATE CONSTRAINT species_name IF NOT EXISTS FOR (s:Species) REQUIRE s.name IS UNIQUE")
q(S, "I3.1b", "Ograniczenie unikatowości Island",
  "CREATE CONSTRAINT island_name IF NOT EXISTS FOR (i:Island) REQUIRE i.name IS UNIQUE")
q(S, "I3.2", "Import LOAD CSV", '''
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
CREATE (p)-[:LIVES_ON]->(i)''')
q(S, "I3.3a", "Liczba pingwinów", "MATCH (p:Penguin) RETURN count(p) AS cnt")
q(S, "I3.3b", "Gatunki", "MATCH (s:Species) RETURN s.name AS name ORDER BY s.name")
q(S, "I3.3c", "Relacje wg typu", "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS cnt")
q(S, "I3.4", "Fragment grafu (liczba ścieżek, w Browserze widok Graph)", '''
MATCH path = (p:Penguin)-[:OF_SPECIES|LIVES_ON]->()
RETURN count(path) AS paths''')

# ---------------------------------------------------------------- Ćw. 4 (instrukcja)
S = "Instrukcja – Ćwiczenie 4: zapytania wyszukujące"
q(S, "I4.1", "Pingwiny Adelie", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(:Species {name: "Adelie"})
RETURN count(p) AS cnt''')
q(S, "I4.2", "Masa > 4500", "MATCH (p:Penguin) WHERE p.body_mass_g > 4500 RETURN count(p) AS cnt")
q(S, "I4.3", "Samice Gentoo", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE s.name = "Gentoo" AND p.sex = "female"
RETURN count(p) AS cnt''')
q(S, "I4.4a", "Wyspy Dream/Torgersen", '''
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE i.name IN ["Dream", "Torgersen"]
RETURN count(p) AS cnt''')
q(S, "I4.4b", "Gatunki Adelie/Chinstrap", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE s.name IN ["Adelie", "Chinstrap"]
RETURN count(p) AS cnt''')
q(S, "I4.5", "5 najcięższych", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species),
      (p)-[:LIVES_ON]->(i:Island)
WHERE p.body_mass_g IS NOT NULL
RETURN s.name AS species, i.name AS island,
       p.sex AS sex, p.body_mass_g AS mass
ORDER BY mass DESC
LIMIT 5''')
q(S, "I4.5b", "To samo BEZ filtra IS NOT NULL (null na początku)", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species),
      (p)-[:LIVES_ON]->(i:Island)
RETURN s.name AS species, i.name AS island,
       p.sex AS sex, p.body_mass_g AS mass
ORDER BY mass DESC
LIMIT 5''')
q(S, "I4.6", "Brak płci", "MATCH (p:Penguin) WHERE p.sex IS NULL RETURN count(p) AS cnt")
q(S, "I4.7", "Unikatowe wyspy", '''
MATCH (:Penguin)-[:LIVES_ON]->(i:Island)
RETURN DISTINCT i.name AS island''')

# ---------------------------------------------------------------- Ćw. 5 (instrukcja)
S = "Instrukcja – Ćwiczenie 5: zapytania agregacyjne"
q(S, "I5.1", "Średnia masa wg gatunku", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
RETURN s.name AS species,
       round(avg(p.body_mass_g), 2) AS avg_mass,
       count(p) AS cnt
ORDER BY avg_mass DESC''')
q(S, "I5.2", "Średnia masa samic wg gatunku", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE p.sex = "female"
RETURN s.name AS species,
       round(avg(p.body_mass_g), 2) AS avg_mass,
       count(p) AS cnt
ORDER BY avg_mass DESC''')
q(S, "I5.3", "Pary gatunek-wyspa", '''
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)
      -[:LIVES_ON]->(i:Island)
RETURN s.name AS species, i.name AS island,
       count(p) AS cnt
ORDER BY cnt DESC''')
q(S, "I5.4", "HAVING: wyspy > 100", '''
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
WITH i.name AS island, count(p) AS cnt
WHERE cnt > 100
RETURN island, cnt
ORDER BY cnt DESC''')
q(S, "I5.5", "collect: gatunki na wyspach", '''
MATCH (s:Species)<-[:OF_SPECIES]-(:Penguin)
      -[:LIVES_ON]->(i:Island)
RETURN i.name AS island,
       collect(DISTINCT s.name) AS species''')

# ---------------------------------------------------------------- Ćw. 6 (instrukcja)
S = "Instrukcja – Ćwiczenie 6: wzorce ścieżek"
q(S, "I6.1", "Gatunki dzielące wyspę z Adelie", '''
MATCH (:Species {name: "Adelie"})<-[:OF_SPECIES]-(:Penguin)
      -[:LIVES_ON]->(i:Island)<-[:LIVES_ON]-(:Penguin)
      -[:OF_SPECIES]->(s2:Species)
WHERE s2.name <> "Adelie"
RETURN DISTINCT i.name AS island, s2.name AS species''')
q(S, "I6.2", "Wyspy z > 1 gatunkiem", '''
MATCH (s:Species)<-[:OF_SPECIES]-(:Penguin)
      -[:LIVES_ON]->(i:Island)
WITH i.name AS island,
     collect(DISTINCT s.name) AS species
WHERE size(species) > 1
RETURN island, species''')

# ================================================================ ĆWICZENIA SAMODZIELNE
S = "Ćwiczenie samodzielne nr 1: zapytania wyszukujące"
q(S, "S1.1", "Chinstrap z Dream, masa > 3500 g – lista", '''
MATCH (s:Species {name: "Chinstrap"})<-[:OF_SPECIES]-(p:Penguin)
      -[:LIVES_ON]->(i:Island {name: "Dream"})
WHERE p.body_mass_g > 3500
RETURN p.sex AS sex, p.bill_length_mm AS bill_length_mm,
       p.flipper_length_mm AS flipper_length_mm,
       p.body_mass_g AS body_mass_g, p.year AS year
ORDER BY body_mass_g DESC''')
q(S, "S1.1b", "Chinstrap z Dream, masa > 3500 g – liczba", '''
MATCH (:Species {name: "Chinstrap"})<-[:OF_SPECIES]-(p:Penguin)
      -[:LIVES_ON]->(:Island {name: "Dream"})
WHERE p.body_mass_g > 3500
RETURN count(p) AS cnt''')
q(S, "S1.2", "10 pingwinów o najdłuższym dziobie", '''
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.bill_length_mm IS NOT NULL
RETURN s.name AS species, i.name AS island,
       p.bill_length_mm AS bill_length_mm
ORDER BY bill_length_mm DESC
LIMIT 10''')
q(S, "S1.3", "Rok 2007, Torgersen lub Biscoe – lista", '''
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.year = 2007 AND i.name IN ["Torgersen", "Biscoe"]
RETURN i.name AS island, s.name AS species, p.sex AS sex,
       p.body_mass_g AS body_mass_g
ORDER BY island, species''')
q(S, "S1.3b", "Rok 2007, Torgersen lub Biscoe – liczba (z podziałem)", '''
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.year = 2007 AND i.name IN ["Torgersen", "Biscoe"]
RETURN i.name AS island, count(p) AS cnt
ORDER BY island''')
q(S, "S1.3c", "Rok 2007, Torgersen lub Biscoe – liczba łączna", '''
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.year = 2007 AND i.name IN ["Torgersen", "Biscoe"]
RETURN count(p) AS cnt''')
q(S, "S1.4", "Pingwiny bez informacji o płci", '''
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.sex IS NULL
RETURN s.name AS species, i.name AS island, p.year AS year,
       p.body_mass_g AS body_mass_g, p.bill_length_mm AS bill_length_mm
ORDER BY species, island''')
q(S, "S1.4b", "Braki płci wg gatunku i wyspy", '''
MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)
WHERE p.sex IS NULL
RETURN s.name AS species, i.name AS island, count(p) AS missing_sex
ORDER BY missing_sex DESC''')
q(S, "S1.5", "Masa 3000–3500 g włącznie", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE 3000 <= p.body_mass_g <= 3500
RETURN s.name AS species, p.sex AS sex, p.body_mass_g AS body_mass_g
ORDER BY body_mass_g ASC''')
q(S, "S1.5b", "Masa 3000–3500 g – liczba", '''
MATCH (p:Penguin)
WHERE p.body_mass_g >= 3000 AND p.body_mass_g <= 3500
RETURN count(p) AS cnt''')

S = "Ćwiczenie samodzielne nr 2: agregacje i wzorce ścieżek"
q(S, "S2.1", "Liczba pingwinów na wyspach", '''
MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)
RETURN i.name AS island, count(p) AS cnt
ORDER BY cnt DESC''')
q(S, "S2.2", "Płetwa wg gatunku i płci", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
WHERE p.sex IS NOT NULL
RETURN s.name AS species, p.sex AS sex,
       round(avg(p.flipper_length_mm), 2) AS avg_flipper,
       min(p.flipper_length_mm) AS min_flipper,
       max(p.flipper_length_mm) AS max_flipper,
       count(p) AS cnt
ORDER BY species, sex''')
q(S, "S2.3", "Średnia masa wg roku", '''
MATCH (p:Penguin)
RETURN p.year AS year,
       round(avg(p.body_mass_g), 2) AS avg_mass,
       count(p.body_mass_g) AS measured, count(p) AS cnt
ORDER BY year''')
q(S, "S2.3b", "Średnia masa wg roku i gatunku (kontrola trendu)", '''
MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)
RETURN s.name AS species, p.year AS year,
       round(avg(p.body_mass_g), 2) AS avg_mass, count(p) AS cnt
ORDER BY species, year''')
q(S, "S2.4", "Wyspy z > 50 pingwinami Adelie (WITH … WHERE)", '''
MATCH (:Species {name: "Adelie"})<-[:OF_SPECIES]-(p:Penguin)
      -[:LIVES_ON]->(i:Island)
WITH i.name AS island, count(p) AS adelie_cnt
WHERE adelie_cnt > 50
RETURN island, adelie_cnt
ORDER BY adelie_cnt DESC''')
q(S, "S2.5a", "Lista wysp dla każdego gatunku (collect)", '''
MATCH (s:Species)<-[:OF_SPECIES]-(:Penguin)-[:LIVES_ON]->(i:Island)
RETURN s.name AS species, collect(DISTINCT i.name) AS islands
ORDER BY species''')
q(S, "S2.5b", "Gatunki występujące na tej samej wyspie co Gentoo (wzorzec ścieżki)", '''
MATCH (:Species {name: "Gentoo"})<-[:OF_SPECIES]-(:Penguin)
      -[:LIVES_ON]->(i:Island)<-[:LIVES_ON]-(:Penguin)
      -[:OF_SPECIES]->(s2:Species)
WHERE s2.name <> "Gentoo"
RETURN DISTINCT i.name AS island, s2.name AS species''')


def to_md(df: pd.DataFrame, max_rows=60) -> str:
    if df.empty:
        return "_(brak wierszy – zapytanie modyfikujące)_"
    # węzły -> słownik właściwości
    df = df.apply(lambda col: col.map(lambda v: dict(v) if hasattr(v, "labels") else v))
    extra = ""
    if len(df) > max_rows:
        extra = f"\n\n_… pokazano {max_rows} z {len(df)} wierszy_"
        df = df.head(max_rows)
    return df.to_markdown(index=False) + extra


def main():
    out = ["# Wyniki zapytań – graf penguins\n"]
    results = {}
    with GraphDatabase.driver(URI, auth=None) as driver:
        driver.verify_connectivity()
        section = None
        for sec, qid, desc, cypher in Q:
            if sec != section:
                out.append(f"\n## {sec}\n")
                section = sec
            df, summary = driver.execute_query(cypher, result_transformer_=lambda r: (r.to_df(), r.consume()))
            c = summary.counters
            stats = {k: v for k, v in vars(c).items() if not k.startswith("_") and v}
            results[qid] = df
            out.append(f"### {qid} – {desc}\n\n```cypher\n{cypher}\n```\n")
            if stats:
                out.append(f"Zmiany: `{stats}`\n")
            out.append(to_md(df) + "\n")
            print(f"{qid}: {len(df)} wierszy {stats if stats else ''}")
    with open("wyniki_penguins.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    pd.to_pickle(results, "wyniki_penguins.pkl")


if __name__ == "__main__":
    main()
