"""Projekt: Graf zakupowy z rekomendacjami – import i zapytania przez sterownik neo4j.

Kroki:
  1. wykonuje import.cypher (LOAD CSV) na serwerze graphdb_projekt (bolt://localhost:7688),
  2. wykonuje 13 zapytań projektowych, zapisuje je do queries.cypher,
     a wyniki do wyniki_projekt.md / wyniki_projekt.pkl,
  3. rysuje wykresy do img/.
Uruchomienie (z katalogu projekt):  uv run --project .. projekt.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from neo4j import GraphDatabase

URI = "bolt://localhost:7688"
HERE = Path(__file__).parent

QUERIES = [
    # (id, typ, wymaganie, opis, zapytanie)
    ("Q1", "agregacja", "W1", "10 najpopularniejszych produktów wg liczby kupujących wraz z przychodem.", """
MATCH (c:Customer)-[b:BOUGHT]->(p:Product)-[:BELONGS_TO]->(cat:Category)
RETURN p.product_id AS id, p.name AS product, cat.name AS category,
       count(DISTINCT c) AS buyers,
       round(sum(b.quantity * p.price), 2) AS revenue
ORDER BY buyers DESC, revenue DESC
LIMIT 10"""),
    ("Q2", "agregacja", "W1", "Liczba transakcji, sztuk i przychód w każdej kategorii.", """
MATCH (:Customer)-[b:BOUGHT]->(p:Product)-[:BELONGS_TO]->(cat:Category)
RETURN cat.name AS category, count(b) AS transactions,
       sum(b.quantity) AS units,
       round(sum(b.quantity * p.price), 2) AS revenue
ORDER BY revenue DESC"""),
    ("Q3", "agregacja (HAVING)", "W4", "Średnia ocena produktów każdej marki – tylko marki z co najmniej 50 ocenami.", """
MATCH (:Customer)-[b:BOUGHT]->(:Product)-[:MADE_BY]->(br:Brand)
WITH br.name AS brand, round(avg(b.rating), 2) AS avg_rating, count(b) AS ratings
WHERE ratings >= 50
RETURN brand, avg_rating, ratings
ORDER BY avg_rating DESC"""),
    ("Q4", "agregacja", "W3", "Liczba klientów, średnie wydatki na klienta i łączny przychód wg miasta.", """
MATCH (city:City)<-[:LIVES_IN]-(c:Customer)-[b:BOUGHT]->(p:Product)
WITH city, c, sum(b.quantity * p.price) AS spent
RETURN city.name AS city, count(c) AS customers,
       round(avg(spent), 2) AS avg_spent_per_customer,
       round(sum(spent), 2) AS revenue
ORDER BY revenue DESC"""),
    ("Q5", "agregacja + collect", "W3", "5 klientów o najwyższych wydatkach z listą kupowanych kategorii.", """
MATCH (c:Customer)-[b:BOUGHT]->(p:Product)-[:BELONGS_TO]->(cat:Category)
RETURN c.customer_id AS id, c.name AS customer,
       round(sum(b.quantity * p.price), 2) AS spent,
       count(b) AS purchases,
       collect(DISTINCT cat.name) AS categories
ORDER BY spent DESC
LIMIT 5"""),
    ("Q6", "wzorzec ścieżki", "W2", "„Klienci, którzy kupili produkt P001, kupili również” – 5 produktów z największą liczbą wspólnych klientów.", """
MATCH (:Product {product_id: "P001"})<-[:BOUGHT]-(c:Customer)-[:BOUGHT]->(other:Product)
WHERE other.product_id <> "P001"
RETURN other.product_id AS id, other.name AS product,
       count(DISTINCT c) AS common_customers
ORDER BY common_customers DESC, id
LIMIT 5"""),
    ("Q7", "wzorzec ścieżki (collaborative filtering)", "W2", "Rekomendacje dla klienta K072: produkty kupione przez klientów o podobnych zakupach, których K072 jeszcze nie ma.", """
MATCH (me:Customer {customer_id: "K072"})-[:BOUGHT]->(p:Product)<-[:BOUGHT]-(peer:Customer)
WITH me, peer, count(DISTINCT p) AS similarity
MATCH (peer)-[b:BOUGHT]->(rec:Product)
WHERE NOT (me)-[:BOUGHT]->(rec) AND b.rating >= 4
MATCH (rec)-[:BELONGS_TO]->(cat:Category)
RETURN rec.product_id AS id, rec.name AS product, cat.name AS category,
       sum(similarity) AS score, count(DISTINCT peer) AS peers
ORDER BY score DESC, peers DESC
LIMIT 5"""),
    ("Q8", "shortestPath", "W5", "Najkrótszy łańcuch obserwowania (FOLLOWS) od klienta K072 do klienta K031.", """
MATCH path = shortestPath(
  (a:Customer {customer_id: "K072"})-[:FOLLOWS*..10]->(b:Customer {customer_id: "K031"}))
RETURN [n IN nodes(path) | n.customer_id + " " + n.name] AS chain,
       length(path) AS hops"""),
    ("Q9", "ścieżka o zmiennej długości", "W5", "Zasięg wpływu: 5 klientów, do których najwięcej osób dociera w 1–3 krokach FOLLOWS (influencerzy).", """
MATCH (influencer:Customer)<-[:FOLLOWS*1..3]-(fan:Customer)
WHERE fan <> influencer
RETURN influencer.customer_id AS id, influencer.name AS customer,
       count(DISTINCT fan) AS reach_3_hops
ORDER BY reach_3_hops DESC
LIMIT 5"""),
    ("Q10", "ścieżka o zmiennej długości", "W2/W5", "Rekomendacje społeczne dla K072: produkty ocenione na 5 przez osoby obserwowane przez K072 w 1–2 krokach.", """
MATCH (me:Customer {customer_id: "K072"})-[:FOLLOWS*1..2]->(friend:Customer)-[b:BOUGHT]->(p:Product)
WHERE b.rating = 5 AND NOT (me)-[:BOUGHT]->(p) AND friend <> me
RETURN p.product_id AS id, p.name AS product,
       collect(DISTINCT friend.name) AS recommended_by
ORDER BY size(recommended_by) DESC, id
LIMIT 5"""),
    ("Q11", "agregacja (HAVING)", "W3", "Klienci kupujący w co najmniej 5 kategoriach (kandydaci do cross-sellingu).", """
MATCH (c:Customer)-[:BOUGHT]->(:Product)-[:BELONGS_TO]->(cat:Category)
WITH c, count(DISTINCT cat) AS n_categories, collect(DISTINCT cat.name) AS categories
WHERE n_categories >= 5
RETURN c.customer_id AS id, c.name AS customer, n_categories, categories
ORDER BY n_categories DESC, id"""),
    ("Q12", "agregacja", "W6", "Kwartalna liczba transakcji i przychód (trend sprzedaży).", """
MATCH (:Customer)-[b:BOUGHT]->(p:Product)
WITH b.date.year AS year, b.date.quarter AS quarter, b, p
RETURN year, quarter, count(b) AS transactions,
       round(sum(b.quantity * p.price), 2) AS revenue
ORDER BY year, quarter"""),
    ("Q13", "wyszukujące (OPTIONAL MATCH)", "W1", "Produkty o najsłabszej sprzedaży – kupione przez mniej niż 4 klientów (kandydaci do przeceny lub wycofania).", """
MATCH (p:Product)-[:BELONGS_TO]->(cat:Category)
OPTIONAL MATCH (c:Customer)-[:BOUGHT]->(p)
WITH p, cat, count(c) AS buyers
WHERE buyers < 4
RETURN p.product_id AS id, p.name AS product, cat.name AS category,
       p.price AS price, buyers
ORDER BY buyers, category"""),
]


def run_import(driver):
    text = (HERE / "import.cypher").read_text(encoding="utf-8")
    stmts = [s.strip() for s in "\n".join(
        l for l in text.splitlines() if not l.strip().startswith("//")).split(";") if s.strip()]
    for s in stmts:
        recs, summary, _ = driver.execute_query(s)
        if recs:
            print(pd.DataFrame([r.data() for r in recs]).to_string(index=False))
    return stmts


def main():
    results = {}
    md = ["# Wyniki zapytań – projekt „Graf zakupowy z rekomendacjami”\n"]
    with GraphDatabase.driver(URI, auth=None) as driver:
        driver.verify_connectivity()
        run_import(driver)
        for label_q, title in [
            ("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY cnt DESC", "Węzły"),
            ("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS cnt ORDER BY cnt DESC", "Relacje")]:
            df = driver.execute_query(label_q, result_transformer_=lambda r: r.to_df())
            results[title] = df
            md.append(f"## {title} po imporcie\n\n```cypher\n{label_q}\n```\n\n{df.to_markdown(index=False)}\n")
        cy = ["// Projekt: Graf zakupowy z rekomendacjami – zapytania", ""]
        for qid, kind, req, desc, query in QUERIES:
            df = driver.execute_query(query.strip(), result_transformer_=lambda r: r.to_df())
            results[qid] = df
            md.append(f"## {qid} [{kind}, {req}]\n\n{desc}\n\n```cypher\n{query.strip()}\n```\n\n"
                      f"{df.to_markdown(index=False) if not df.empty else '_(brak wyników)_'}\n")
            cy += [f"// {qid} [{kind}] – {desc}", query.strip() + ";", ""]
            print(f"{qid}: {len(df)} wierszy")
    (HERE / "queries.cypher").write_text("\n".join(cy), encoding="utf-8")
    (HERE / "wyniki_projekt.md").write_text("\n".join(md), encoding="utf-8")
    pd.to_pickle(results, HERE / "wyniki_projekt.pkl")
    plots(results)


def plots(r):
    sns.set_theme(style="whitegrid")
    img = HERE / "img"
    img.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(data=r["Q2"], y="category", x="revenue", color="#4393c3", ax=ax)
    ax.set_xlabel("Przychód [zł]"); ax.set_ylabel("Kategoria")
    ax.set_title("Przychód wg kategorii produktów (Q2)")
    fig.savefig(img / "q2_revenue_by_category.png", dpi=150, bbox_inches="tight"); plt.close(fig)

    q12 = r["Q12"].copy()
    q12["okres"] = q12["year"].astype(str) + " Q" + q12["quarter"].astype(str)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=q12, x="okres", y="revenue", marker="o", ax=ax)
    ax.set_xlabel("Kwartał"); ax.set_ylabel("Przychód [zł]")
    ax.set_title("Kwartalny przychód (Q12)")
    fig.savefig(img / "q12_revenue_trend.png", dpi=150, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    main()
