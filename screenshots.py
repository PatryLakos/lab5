"""Automatyczne zrzuty ekranu wyników zapytań z Neo4j Browser (Playwright + Edge).

uv run screenshots.py            -> zrzuty dla grafu penguins (port 7474)
uv run screenshots.py projekt    -> zrzuty dla grafu projektu (port 7475 / bolt 7688)
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PENGUINS = [
    ("cw1_cypher_shell", None, None),  # zrzut terminala robiony osobno
    ("cw3_weryfikacja", "MATCH ()-[r]->() RETURN type(r), count(r)", "table"),
    ("cw3_graf", "MATCH path = (p:Penguin)-[:OF_SPECIES|LIVES_ON]->()\nRETURN path LIMIT 50", "graph"),
    ("cw4_top5", 'MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species),\n      (p)-[:LIVES_ON]->(i:Island)\nWHERE p.body_mass_g IS NOT NULL\nRETURN s.name AS species, i.name AS island,\n       p.sex AS sex, p.body_mass_g AS mass\nORDER BY mass DESC\nLIMIT 5', "table"),
    ("cw5_collect", 'MATCH (s:Species)<-[:OF_SPECIES]-(:Penguin)\n      -[:LIVES_ON]->(i:Island)\nRETURN i.name AS island,\n       collect(DISTINCT s.name) AS species', "table"),
    ("cw6_adelie", 'MATCH (:Species {name: "Adelie"})<-[:OF_SPECIES]-(:Penguin)\n      -[:LIVES_ON]->(i:Island)<-[:LIVES_ON]-(:Penguin)\n      -[:OF_SPECIES]->(s2:Species)\nWHERE s2.name <> "Adelie"\nRETURN DISTINCT i.name AS island, s2.name AS species', "table"),
    # ćwiczenia samodzielne
    ("s1_1", 'MATCH (:Species {name: "Chinstrap"})<-[:OF_SPECIES]-(p:Penguin)\n      -[:LIVES_ON]->(:Island {name: "Dream"})\nWHERE p.body_mass_g > 3500\nRETURN p.sex AS sex, p.bill_length_mm AS bill, p.flipper_length_mm AS flipper,\n       p.body_mass_g AS mass, p.year AS year\nORDER BY mass DESC', "table"),
    ("s1_1_count", 'MATCH (:Species {name: "Chinstrap"})<-[:OF_SPECIES]-(p:Penguin)\n      -[:LIVES_ON]->(:Island {name: "Dream"})\nWHERE p.body_mass_g > 3500\nRETURN count(p) AS cnt', "table"),
    ("s1_2", 'MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)\nWHERE p.bill_length_mm IS NOT NULL\nRETURN s.name AS species, i.name AS island,\n       p.bill_length_mm AS bill_length_mm\nORDER BY bill_length_mm DESC\nLIMIT 10', "table"),
    ("s1_3", 'MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)\nWHERE p.year = 2007 AND i.name IN ["Torgersen", "Biscoe"]\nRETURN i.name AS island, s.name AS species, p.sex AS sex,\n       p.body_mass_g AS body_mass_g\nORDER BY island, species', "table"),
    ("s1_3_count", 'MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)\nWHERE p.year = 2007 AND i.name IN ["Torgersen", "Biscoe"]\nRETURN count(p) AS cnt', "table"),
    ("s1_4", 'MATCH (s:Species)<-[:OF_SPECIES]-(p:Penguin)-[:LIVES_ON]->(i:Island)\nWHERE p.sex IS NULL\nRETURN s.name AS species, i.name AS island, p.year AS year,\n       p.body_mass_g AS body_mass_g, p.bill_length_mm AS bill_length_mm\nORDER BY species, island', "table"),
    ("s1_5", 'MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)\nWHERE 3000 <= p.body_mass_g <= 3500\nRETURN s.name AS species, p.sex AS sex, p.body_mass_g AS body_mass_g\nORDER BY body_mass_g ASC', "table"),
    ("s2_1", 'MATCH (p:Penguin)-[:LIVES_ON]->(i:Island)\nRETURN i.name AS island, count(p) AS cnt\nORDER BY cnt DESC', "table"),
    ("s2_2", 'MATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)\nWHERE p.sex IS NOT NULL\nRETURN s.name AS species, p.sex AS sex,\n       round(avg(p.flipper_length_mm), 2) AS avg_flipper,\n       min(p.flipper_length_mm) AS min_flipper,\n       max(p.flipper_length_mm) AS max_flipper\nORDER BY species, sex', "table"),
    ("s2_3", 'MATCH (p:Penguin)\nRETURN p.year AS year,\n       round(avg(p.body_mass_g), 2) AS avg_mass,\n       count(p) AS cnt\nORDER BY year', "table"),
    ("s2_4", 'MATCH (:Species {name: "Adelie"})<-[:OF_SPECIES]-(p:Penguin)\n      -[:LIVES_ON]->(i:Island)\nWITH i.name AS island, count(p) AS adelie_cnt\nWHERE adelie_cnt > 50\nRETURN island, adelie_cnt\nORDER BY adelie_cnt DESC', "table"),
    ("s2_5a", 'MATCH (s:Species)<-[:OF_SPECIES]-(:Penguin)-[:LIVES_ON]->(i:Island)\nRETURN s.name AS species, collect(DISTINCT i.name) AS islands\nORDER BY species', "table"),
    ("s2_5b", 'MATCH (:Species {name: "Gentoo"})<-[:OF_SPECIES]-(:Penguin)\n      -[:LIVES_ON]->(i:Island)<-[:LIVES_ON]-(:Penguin)\n      -[:OF_SPECIES]->(s2:Species)\nWHERE s2.name <> "Gentoo"\nRETURN DISTINCT i.name AS island, s2.name AS species', "table"),
]


def projekt_shots():
    sys.path.insert(0, str(Path(__file__).parent / "projekt"))
    from projekt import QUERIES
    shots = [
        ("p_import_nodes", "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY cnt DESC", "table"),
        ("p_import_rels", "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS cnt ORDER BY cnt DESC", "table"),
        ("p_schema", "CALL db.schema.visualization()", "graph"),
        ("p_graph_sample", 'MATCH path = (c:Customer {customer_id: "K072"})-[:BOUGHT|LIVES_IN]->(x)\nOPTIONAL MATCH p2 = (x)-[:BELONGS_TO|MADE_BY]->()\nRETURN path, p2', "graph"),
    ]
    for qid, _k, _r, _d, query in QUERIES:
        shots.append((f"p_{qid.lower()}", query.strip(), "table"))
    shots.append(("p_q8_graph", 'MATCH path = shortestPath(\n  (a:Customer {customer_id: "K072"})-[:FOLLOWS*..10]->(b:Customer {customer_id: "K031"}))\nRETURN path', "graph"))
    return shots


def run(url, bolt, shots, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge", headless=True)
        pg = b.new_page(viewport={"width": 1500, "height": 1300})
        pg.goto(url)
        pg.wait_for_timeout(5000)
        if bolt:
            url_box = pg.get_by_label("Connection URL")
            if url_box.count():
                url_box.fill(bolt)
        pg.get_by_role("button", name="Connect", exact=True).click()
        pg.wait_for_timeout(4000)

        def dismiss():
            for label in ("Dismiss", "Skip", "Close"):
                btn = pg.get_by_role("button", name=label, exact=True)
                for i in range(btn.count()):
                    try:
                        btn.nth(i).click(timeout=800)
                    except Exception:
                        pass

        dismiss()
        for name, query, view in shots:
            if query is None:
                continue
            # usuń poprzednie ramki z wynikami
            for btn in pg.get_by_role("button", name="Remove frame").all():
                try:
                    btn.click(timeout=1000)
                except Exception:
                    pass
            ed = pg.locator(".cm-content").first
            ed.click()
            pg.keyboard.press("Control+A")
            pg.keyboard.press("Delete")
            pg.keyboard.insert_text(query)
            pg.get_by_test_id("run-button").click()
            pg.wait_for_timeout(3500 if view == "graph" else 2000)
            dismiss()
            frame = pg.get_by_test_id("frame").first
            if view == "table":
                tab = frame.get_by_text("Table", exact=True)
                if tab.count():
                    tab.first.click()
                    pg.wait_for_timeout(700)
            frame.screenshot(path=str(outdir / f"{name}.png"))
            print("zapisano", name)
        b.close()


if __name__ == "__main__":
    root = Path(__file__).parent
    if len(sys.argv) > 1 and sys.argv[1] == "projekt":
        run("http://localhost:7475/browser/", "localhost:7688", projekt_shots(), root / "projekt" / "img" / "shots")
    else:
        only = sys.argv[1:]
        shots = [s for s in PENGUINS if not only or s[0] in only]
        run("http://localhost:7474/browser/", None, shots, root / "img" / "shots")
