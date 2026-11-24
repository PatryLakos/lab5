"""Buduje sprawozdanie Sprawozdanie_Lab5.docx z wyników zapisanych przez
queries_penguins.py, projekt/projekt.py, analiza.ipynb i screenshots.py."""
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "projekt"))
from queries_penguins import Q as PQ  # noqa: E402
from projekt import QUERIES  # noqa: E402

R = pd.read_pickle(ROOT / "wyniki_penguins.pkl")
RP = pd.read_pickle(ROOT / "projekt" / "wyniki_projekt.pkl")
CY = {qid: cy for _s, qid, _d, cy in PQ}
SHOTS = ROOT / "img" / "shots"
PSHOTS = ROOT / "projekt" / "img" / "shots"

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(11)
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.2)
    s.top_margin = s.bottom_margin = Cm(2)

fig_no = [0]


def h(text, level=1):
    doc.add_heading(text, level=level)


def p(text="", bold=False, italic=False, align=None):
    par = doc.add_paragraph()
    # prosty **pogrubienie** w tekście
    parts = text.split("**")
    for i, part in enumerate(parts):
        run = par.add_run(part)
        run.bold = bold or (i % 2 == 1)
        run.italic = italic
    if align:
        par.alignment = align
    return par


def bullet(text):
    par = doc.add_paragraph(style="List Bullet")
    parts = text.split("**")
    for i, part in enumerate(parts):
        par.add_run(part).bold = i % 2 == 1


def shade(par, color="F2F2F2"):
    pPr = par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    pPr.append(shd)


def code(text):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(6)
    run = par.add_run(text.strip("\n"))
    run.font.name = "Consolas"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    run.font.size = Pt(9)
    shade(par)
    return par


def cypher(qid):
    code(CY[qid])


def table(df, max_rows=25, font=9):
    df = df.copy()
    note = None
    if len(df) > max_rows:
        note = f"(pokazano {max_rows} z {len(df)} wierszy)"
        df = df.head(max_rows)
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, c in enumerate(df.columns):
        t.rows[0].cells[i].text = str(c)
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for i, v in enumerate(row):
            if isinstance(v, float) and pd.isna(v):
                s = "null"
            elif isinstance(v, list):
                s = ", ".join(map(str, v))
            elif isinstance(v, float) and v.is_integer() and abs(v) < 1e5:
                s = str(int(v))
            else:
                s = str(v)
            cells[i].text = s
    for row in t.rows:
        for c in row.cells:
            for par in c.paragraphs:
                for run in par.runs:
                    run.font.size = Pt(font)
    if note:
        p(note, italic=True)
    doc.add_paragraph()


def image(path, caption, width=16):
    if not Path(path).exists():
        p(f"[brak pliku {path}]", italic=True)
        return
    doc.add_picture(str(path), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    fig_no[0] += 1
    cap = p(f"Rysunek {fig_no[0]}. {caption}", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    cap.runs[0].font.size = Pt(9)


def answer(text):
    par = doc.add_paragraph()
    par.add_run("Odpowiedź: ").bold = True
    par.add_run(text)
    shade(par, "E8F1FA")


# =============================================================== STRONA TYTUŁOWA
for _ in range(4):
    doc.add_paragraph()
p("Bazy danych dla sztucznej inteligencji", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER).runs[0].font.size = Pt(16)
p("Sprawozdanie – Laboratorium nr 5", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER).runs[0].font.size = Pt(20)
p("Utworzenie i zarządzanie grafową bazą danych. Realizacja zapytań.", italic=True,
  align=WD_ALIGN_PARAGRAPH.CENTER).runs[0].font.size = Pt(13)
for _ in range(6):
    doc.add_paragraph()
p("Autor: Patryk Kaniosz", align=WD_ALIGN_PARAGRAPH.RIGHT)
p("Grupa: ………", align=WD_ALIGN_PARAGRAPH.RIGHT)
p(f"Data: {date.today():%d.%m.%Y}", align=WD_ALIGN_PARAGRAPH.RIGHT)
doc.add_page_break()

# =============================================================== CEL
h("1. Cel laboratorium")
p("Celem laboratorium było praktyczne opanowanie pracy z grafową bazą danych Neo4j: uruchomienie "
  "serwera w kontenerze Docker, zamodelowanie zbioru Palmer Penguins jako grafu własności, import "
  "danych klauzulą LOAD CSV, tworzenie i modyfikowanie węzłów i relacji oraz realizacja zapytań "
  "wyszukujących, agregacyjnych i opartych na wzorcach ścieżek w języku Cypher – w Neo4j Browser "
  "i z poziomu Pythona (sterownik neo4j). Dodatkowo zaprojektowano własną grafową bazę danych "
  "(projekt zespołowy).")
h("Środowisko", 2)
bullet("Docker Desktop 28.1.1, obraz **neo4j:2026-community** (kontenery graphdb i graphdb_projekt),")
bullet("Neo4j Browser (http://localhost:7474 oraz :7475 dla projektu), cypher-shell,")
bullet("Python 3.13 + menedżer UV, biblioteki: neo4j, pandas, seaborn, matplotlib, ipykernel,")
bullet("zbiór danych Palmer Penguins (344 obserwacje, licencja CC0) w pliku data/penguins.csv.")
p("Struktura katalogu roboczego:")
code("lab5\n│   docker-compose.yml        – serwer Neo4j dla grafu penguins\n│   queries_penguins.py       – wszystkie zapytania Cypher (ćw. 2-6 i samodzielne 1-2)\n"
     "│   analiza.ipynb             – ćw. 7 i ćwiczenie samodzielne 3\n│   wyniki_penguins.md        – pełne wyniki zapytań\n"
     "├───data\n│       penguins.csv\n└───projekt                  – projekt zespołowy (osobny kontener)\n"
     "    │   docker-compose.yml, generate_data.py, import.cypher, queries.cypher, projekt.py\n    └───data  (*.csv)")

# =============================================================== CZĘŚĆ INSTRUKCYJNA
h("2. Realizacja ćwiczeń z instrukcji")

h("Ćwiczenie 1 – uruchomienie serwera Neo4j w kontenerze Docker", 2)
p("Plik docker-compose.yml definiuje usługę opartą na obrazie neo4j:2026-community z kontenerem graphdb, "
  "portami 7474 (Neo4j Browser) i 7687 (Bolt), wyłączonym uwierzytelnianiem (NEO4J_AUTH=none), "
  "trwałym wolumenem neo4j_data oraz katalogiem ./data zamontowanym jako katalog importu serwera.")
code((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
p("Uruchomienie kontenera, sprawdzenie jego stanu i testowe zapytanie w konsoli cypher-shell:")
code((ROOT / "img" / "cw1_terminal.txt").read_text(encoding="utf-8"))
p("Kontener graphdb działa (status Up), a zapytanie RETURN 1 zwróciło wynik 1 – serwer jest gotowy. "
  "Na liście widoczny jest też drugi kontener graphdb_projekt używany w projekcie zespołowym.")

h("Ćwiczenie 2 – Neo4j Browser, pierwsze kroki w Cypher", 2)
p("Po połączeniu z serwerem (No authentication) utworzono testowy węzeł Penguin, węzeł Island "
  "i relację LIVES_ON, a następnie zmodyfikowano i usunięto dane:")
for qid in ["I2.2", "I2.3", "I2.4", "I2.5", "I2.6", "I2.7", "I2.7b", "I2.8"]:
    cypher(qid)
p("Wynik SET: węzeł ma właściwości body_mass_g = 3950, verified = true. Pojedyncze DELETE na węźle "
  "z relacją zakończyłoby się błędem – dlatego pingwina usunięto przez DETACH DELETE (usunięto 1 węzeł "
  "i 1 relację), a wyspę, już bez relacji, zwykłym DELETE. Ostatnie zapytanie zwróciło count(n) = "
  f"{int(R['I2.8'].iloc[0, 0])} – graf jest pusty.")

h("Ćwiczenie 3 – model grafu i import LOAD CSV", 2)
p("Model: węzły Penguin (344, pomiary + sex, year), Species (3) i Island (3), relacje "
  "(:Penguin)-[:OF_SPECIES]->(:Species) i (:Penguin)-[:LIVES_ON]->(:Island). "
  "Najpierw utworzono ograniczenia unikatowości, potem zaimportowano dane:")
cypher("I3.1a"); cypher("I3.1b"); cypher("I3.2")
p("Import utworzył 350 węzłów (344 + 3 + 3) i 688 relacji. Weryfikacja:")
cypher("I3.3a")
p(f"Wynik: {int(R['I3.3a'].iloc[0, 0])} węzłów Penguin.")
cypher("I3.3b")
p("Wynik: " + ", ".join(f'"{n}"' for n in R["I3.3b"]["name"]) + ".")
cypher("I3.3c")
table(R["I3.3c"])
image(SHOTS / "cw3_weryfikacja.png", "Weryfikacja liczby relacji po imporcie (Neo4j Browser).", 14)
image(SHOTS / "cw3_graf.png", "Fragment grafu penguins w widoku Graph (50 ścieżek).", 15)

h("Ćwiczenie 4 – zapytania wyszukujące", 2)
rows = [
    ("I4.1", "Adelie", 'countDocuments({species: "Adelie"})'),
    ("I4.2", "masa > 4500 g", "{body_mass_g: {$gt: 4500}}"),
    ("I4.3", "samice Gentoo", '{species: "Gentoo", sex: "female"}'),
    ("I4.4a", "wyspy Dream/Torgersen", '{island: {$in: ["Dream","Torgersen"]}}'),
    ("I4.4b", "gatunki Adelie/Chinstrap", '{species: {$in: ["Adelie","Chinstrap"]}}'),
    ("I4.6", "brak płci", "countDocuments({sex: null})"),
]
for qid, *_ in rows:
    cypher(qid)
table(pd.DataFrame([(d, int(R[q].iloc[0, 0]), m) for q, d, m in rows],
                   columns=["zapytanie", "wynik Cypher", "odpowiednik MongoDB"]))
p("Pięć najcięższych pingwinów (projekcja, aliasy, sortowanie, LIMIT):")
cypher("I4.5")
image(SHOTS / "cw4_top5.png", "Pięć najcięższych pingwinów – sortowanie i LIMIT.", 15)
p("Bez warunku IS NOT NULL listę otwierają dwa pingwiny bez pomiaru masy – Cypher przy sortowaniu "
  "malejącym umieszcza null na początku:")
table(R["I4.5b"])
cypher("I4.7")
table(R["I4.7"])

h("Ćwiczenie 5 – zapytania agregacyjne", 2)
for qid, txt in [("I5.1", "Średnia masa ciała wg gatunku (s.name jest kluczem grupowania):"),
                 ("I5.2", "Średnia masa samic wg gatunku (WHERE przed agregacją = $match przed $group):"),
                 ("I5.3", "Liczba obserwacji dla par gatunek–wyspa:"),
                 ("I5.4", "Odpowiednik HAVING – WITH + WHERE (wyspy z > 100 obserwacjami):"),
                 ("I5.5", "Funkcja collect – gatunki na wyspach:")]:
    p(txt); cypher(qid); table(R[qid])
image(SHOTS / "cw5_collect.png", "Wynik zapytania agregacyjnego z funkcją collect.", 15)
p("Wyniki są identyczne z podanymi w instrukcji (np. Gentoo 5076,02 g / 124 osobniki). Funkcja avg "
  "pomija null – średnia Adelie liczona jest ze 151 pomiarów przy 152 węzłach.")

h("Ćwiczenie 6 – wzorce ścieżek i porównanie modeli", 2)
cypher("I6.1"); table(R["I6.1"])
image(SHOTS / "cw6_adelie.png", "Gatunki dzielące wyspę z gatunkiem Adelie – jeden wzorzec ścieżki.", 15)
cypher("I6.2"); table(R["I6.2"])
p("W modelu dokumentowym gatunek i wyspa są polami powtarzanymi w każdym dokumencie, a pytanie "
  "„z kim Adelie dzieli wyspy” wymaga dwóch zapytań lub złożonej agregacji. W grafie te same informacje "
  "są relacjami do wspólnych węzłów, więc wystarczy jeden wzorzec ścieżki "
  "Species←Penguin→Island←Penguin→Species.")

h("Ćwiczenie 7 – Neo4j w Pythonie (sterownik neo4j)", 2)
code("uv init .\nuv add neo4j pandas seaborn matplotlib ipykernel")
code('from neo4j import GraphDatabase, Result\n\ndriver = GraphDatabase.driver("bolt://localhost:7687", auth=None)\n'
     'driver.verify_connectivity()\n\nquery = """\nMATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)\n'
     'RETURN s.name AS species, round(avg(p.body_mass_g), 2) AS avg_mass, count(p) AS cnt\n'
     'ORDER BY avg_mass DESC\n"""\ndf = driver.execute_query(query, result_transformer_=Result.to_df)\nprint(df)\n\n'
     'import seaborn as sns\nimport matplotlib.pyplot as plt\nsns.barplot(data=df, x="species", y="avg_mass")\n'
     'plt.xlabel("Gatunek"); plt.ylabel("Średnia masa ciała [g]")\n'
     'plt.title("Średnia masa ciała według gatunku"); plt.show()')
table(R["I5.1"])
image(ROOT / "img" / "cw7_avg_mass.png", "Średnia masa ciała wg gatunku – wynik zapytania w DataFrame (notatnik analiza.ipynb).", 11)
p("DataFrame zawiera te same wartości, co agregacja $group w MongoDB z Laboratorium nr 4.")

# =============================================================== SAMODZIELNE 1
doc.add_page_break()
h("3. Ćwiczenia samodzielne")
h("Ćwiczenie samodzielne nr 1 – zapytania wyszukujące", 2)

p("**(1)** Pingwiny gatunku Chinstrap z wyspy Dream o masie > 3500 g. Gatunek i wyspa są we wzorcu "
  "ścieżki, warunek liczbowy w WHERE:")
cypher("S1.1")
image(SHOTS / "s1_1.png", "Chinstrap z wyspy Dream o masie > 3500 g (fragment listy, 49 rekordów).", 15)
cypher("S1.1b")
answer(f"takich pingwinów jest {int(R['S1.1b'].iloc[0, 0])} (30 samców i 19 samic). "
       "MongoDB: countDocuments({species: \"Chinstrap\", island: \"Dream\", body_mass_g: {$gt: 3500}}).")

p("**(2)** 10 pingwinów o najdłuższym dziobie (pominięto węzły bez pomiaru):")
cypher("S1.2")
table(R["S1.2"])
image(SHOTS / "s1_2.png", "10 pingwinów o najdłuższym dziobie.", 15)
answer("najdłuższy dziób (59,6 mm) ma pingwin Gentoo z Biscoe; w pierwszej dziesiątce jest po 5 osobników "
       "Gentoo (Biscoe) i Chinstrap (Dream), nie ma żadnego Adelie. Warunek IS NOT NULL jest konieczny, bo inaczej "
       "dwa węzły z null znalazłyby się na początku listy.")

p("**(3)** Pingwiny zaobserwowane w 2007 r. na wyspie Torgersen lub Biscoe:")
cypher("S1.3")
table(R["S1.3"], max_rows=12)
image(SHOTS / "s1_3.png", "Pingwiny z 2007 r. z wysp Torgersen i Biscoe (fragment listy).", 15)
cypher("S1.3c")
table(R["S1.3b"])
image(SHOTS / "s1_3_count.png", "Liczba pingwinów z 2007 r. z wysp Torgersen i Biscoe.", 12)
answer(f"{int(R['S1.3c'].iloc[0, 0])} pingwinów – 44 z Biscoe i 20 z Torgersen. "
       "MongoDB: {year: 2007, island: {$in: [\"Torgersen\", \"Biscoe\"]}}.")

p("**(4)** Węzły Penguin bez informacji o płci:")
cypher("S1.4")
table(R["S1.4"])
image(SHOTS / "s1_4.png", "Pingwiny bez informacji o płci.", 15)
cypher("S1.4b")
table(R["S1.4b"])
answer("braków jest 11: Adelie z Torgersen (5) i z Dream (1) oraz Gentoo z Biscoe (5); Chinstrap nie ma braków. "
       "Dwa z tych węzłów (Adelie/Torgersen 2007, Gentoo/Biscoe 2009) nie mają żadnych pomiarów – należy je "
       "usunąć lub oznaczyć (np. etykietą :Incomplete) i wykluczyć z analiz. Pozostałe 9 węzłów warto zachować "
       "w analizach niezależnych od płci, a w analizach według płci pominąć je lub uzupełnić płeć "
       "klasyfikatorem wytrenowanym na masie i wymiarach dzioba w obrębie gatunku (z zaznaczeniem imputacji).")

p("**(5)** Pingwiny o masie od 3000 do 3500 g włącznie, posortowane rosnąco. Cypher pozwala zapisać "
  "przedział jako porównanie łańcuchowe 3000 <= x <= 3500:")
cypher("S1.5")
table(R["S1.5"], max_rows=15)
image(SHOTS / "s1_5.png", "Pingwiny o masie 3000–3500 g (fragment listy).", 15)
answer(f"w przedziale mieści się {int(R['S1.5b'].iloc[0, 0])} pingwinów; najlżejsze mają 3000 g. "
       "MongoDB: {body_mass_g: {$gte: 3000, $lte: 3500}} z sort({body_mass_g: 1}).")

p("**Porównanie z MongoDB (Lab. 4).** Wyniki liczbowe są identyczne. W MongoDB wszystkie warunki "
  "dotyczą pól jednego dokumentu ({species, island, body_mass_g}), w Cypherze gatunek i wyspa są "
  "węzłami, więc warunki na nich zapisuje się we wzorcu ścieżki, a warunki na pomiarach w WHERE. "
  "Operatory $gt/$in/$and zastępują zwykłe >, IN, AND. Inaczej działa sortowanie null – w Cypherze trzeba "
  "jawnie filtrować IS NOT NULL.")

# =============================================================== SAMODZIELNE 2
h("Ćwiczenie samodzielne nr 2 – agregacje i wzorce ścieżek", 2)
p("**(1)** Liczba pingwinów na każdej wyspie:")
cypher("S2.1"); table(R["S2.1"])
image(SHOTS / "s2_1.png", "Liczba pingwinów na wyspach.", 13)
answer("Biscoe – 168, Dream – 124, Torgersen – 52.")

p("**(2)** Średnia, minimalna i maksymalna długość płetwy dla par gatunek–płeć (bez braków płci):")
cypher("S2.2"); table(R["S2.2"])
image(SHOTS / "s2_2.png", "Długość płetwy wg gatunku i płci.", 15)
answer("najdłuższe płetwy mają samce Gentoo (śr. 221,54 mm, 208–231 mm), najkrótsze samice Adelie "
       "(187,79 mm). W każdym gatunku samce mają dłuższe płetwy niż samice.")

p("**(3)** Średnia masa ciała wg roku obserwacji:")
cypher("S2.3"); table(R["S2.3"])
image(SHOTS / "s2_3.png", "Średnia masa ciała wg roku.", 13)
p("Dla kontroli wpływu składu gatunkowego policzono też średnią wg roku i gatunku:")
cypher("S2.3b"); table(R["S2.3b"])
image(ROOT / "img" / "samodz2_trend.png", "Średnia masa ciała wg roku i gatunku.", 12)
answer("nie widać wyraźnego trendu: 4124,5 g (2007) → 4266,7 g (2008) → 4210,3 g (2009). Wzrost w 2008 r. wynika "
       "głównie ze zmiany składu próby (więcej ciężkich Gentoo: 34 osobniki w 2007 r., 46 w 2008 r.). W obrębie "
       "gatunków średnie wahają się o ok. ±100 g bez stałego kierunku, więc przy 3 latach obserwacji nie można "
       "mówić o trendzie.")

p("**(4)** Wyspy, na których zaobserwowano więcej niż 50 pingwinów Adelie (WITH + WHERE = HAVING):")
cypher("S2.4"); table(R["S2.4"])
image(SHOTS / "s2_4.png", "Wyspy z ponad 50 pingwinami Adelie.", 13)
answer("Dream (56) i Torgersen (52); Biscoe odpada (44 osobniki Adelie).")

p("**(5)** Lista wysp dla każdego gatunku (collect) oraz gatunki dzielące wyspę z Gentoo (wzorzec ścieżki):")
cypher("S2.5a"); table(R["S2.5a"])
image(SHOTS / "s2_5a.png", "Wyspy zamieszkiwane przez poszczególne gatunki.", 14)
cypher("S2.5b"); table(R["S2.5b"])
image(SHOTS / "s2_5b.png", "Gatunek występujący na tej samej wyspie co Gentoo.", 13)
answer("Adelie występuje na wszystkich trzech wyspach, Chinstrap tylko na Dream, Gentoo tylko na Biscoe. "
       "Na tej samej wyspie co Gentoo (Biscoe) występuje wyłącznie gatunek Adelie.")

p("**Porównanie z MongoDB.** Grupowanie w Cypherze jest niejawne (klucz = nieagregowane wyrażenia w RETURN/WITH), "
  "w MongoDB jawne ($group z _id). HAVING to w Mongo kolejny etap $match po $group, w Cypherze WITH … WHERE. "
  "collect(DISTINCT) odpowiada $addToSet. Zadanie (5b) w MongoDB wymaga dwóch zapytań (wyspy Gentoo, potem "
  "gatunki na tych wyspach) albo $lookup na tej samej kolekcji – w grafie jest to jeden wzorzec ścieżki.")

# =============================================================== SAMODZIELNE 3
h("Ćwiczenie samodzielne nr 3 – sterownik neo4j i wizualizacja", 2)
p("Wybrano zapytanie agregacyjne z ćwiczenia 2 (2) – długość płetwy wg gatunku i płci. Zapytanie wykonano "
  "w notatniku analiza.ipynb, wynik trafił do DataFrame, a wykres przygotowano w Seaborn:")
code('from neo4j import GraphDatabase, Result\nimport seaborn as sns, matplotlib.pyplot as plt\n\n'
     'driver = GraphDatabase.driver("bolt://localhost:7687", auth=None)\n'
     'query_flipper = """\nMATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)\nWHERE p.sex IS NOT NULL\n'
     'RETURN s.name AS species, p.sex AS sex,\n       round(avg(p.flipper_length_mm), 2) AS avg_flipper,\n'
     '       min(p.flipper_length_mm) AS min_flipper,\n       max(p.flipper_length_mm) AS max_flipper,\n'
     '       count(p) AS cnt\nORDER BY species, sex\n"""\n'
     'df_f = driver.execute_query(query_flipper, result_transformer_=Result.to_df)\n\n'
     'fig, ax = plt.subplots(figsize=(8, 5))\n'
     'sns.barplot(data=df_f, x="species", y="avg_flipper", hue="sex", ax=ax)\n'
     '# wąsy min–max dla każdego słupka (ax.errorbar), etykiety wartości (ax.bar_label)\n'
     'ax.set_xlabel("Gatunek"); ax.set_ylabel("Długość płetwy [mm]")\n'
     'ax.set_title("Średnia długość płetwy wg gatunku i płci (wąsy: min–max)")\nplt.show()')
table(R["S2.2"])
image(ROOT / "img" / "samodz3_flipper.png", "Średnia długość płetwy wg gatunku i płci (wąsy: zakres min–max).", 14)
p("**Interpretacja.** Gentoo ma wyraźnie najdłuższe płetwy (średnio ok. 213 mm u samic i 222 mm u samców), "
  "o ponad 20 mm więcej niż Adelie i Chinstrap, których zakresy w dużej mierze się pokrywają. W każdym gatunku "
  "samce mają dłuższe płetwy od samic (o ok. 5–9 mm), co potwierdza dymorfizm płciowy. Długość płetwy dobrze "
  "odróżnia Gentoo od pozostałych gatunków, ale słabo rozdziela Adelie i Chinstrap – do tego potrzebne są inne "
  "cechy (np. długość dzioba).")

# =============================================================== PROJEKT
doc.add_page_break()
h("4. Ćwiczenie samodzielne nr 4 – projekt: graf zakupowy z rekomendacjami")
h("4.1 Opis tematu i wymagania", 2)
p("Baza modeluje sklep internetowy: klientów, kupowane przez nich produkty, kategorie i marki produktów, "
  "miasta klientów oraz sieć obserwowania się klientów (jak w serwisach z recenzjami). Służy do analizy "
  "sprzedaży oraz do generowania rekomendacji – zarówno typu „klienci, którzy kupili ten produkt, kupili "
  "również”, jak i rekomendacji społecznych opartych na osobach obserwowanych przez klienta.")
p("Wymagania funkcjonalne (pytania, na które baza ma odpowiadać):")
for w in ["**W1** – Które produkty i kategorie sprzedają się najlepiej, a które najsłabiej?",
          "**W2** – Jakie produkty polecić klientowi (wspólni klienci, podobni klienci, znajomi)?",
          "**W3** – Którzy klienci i które miasta generują największe przychody; kto kupuje w wielu kategoriach?",
          "**W4** – Jak klienci oceniają produkty poszczególnych marek?",
          "**W5** – Jak klienci są ze sobą powiązani i kto ma największy zasięg wpływu (influencerzy)?",
          "**W6** – Jak zmienia się sprzedaż w czasie?"]:
    bullet(w)

h("4.2 Model grafu", 2)
image(ROOT / "projekt" / "img" / "model.png", "Poglądowy model grafu projektu (etykiety, relacje, właściwości).", 16)
image(PSHOTS / "p_schema.png", "Schemat grafu wygenerowany w Neo4j Browser (CALL db.schema.visualization()).", 14)
table(pd.DataFrame([
    ("węzeł", "Customer", "customer_id, name, age, registered (date)", "200"),
    ("węzeł", "Product", "product_id, name, price", "125"),
    ("węzeł", "Category", "category_id, name", "8"),
    ("węzeł", "Brand", "brand_id, name", "12"),
    ("węzeł", "City", "name, voivodeship", "8"),
    ("relacja", "BOUGHT", "Customer → Product; quantity, date, rating", "1233"),
    ("relacja", "BELONGS_TO", "Product → Category", "125"),
    ("relacja", "MADE_BY", "Product → Brand", "125"),
    ("relacja", "LIVES_IN", "Customer → City", "200"),
    ("relacja", "FOLLOWS", "Customer → Customer", "279"),
], columns=["element", "nazwa", "właściwości / opis", "liczba"]))
p("**Uzasadnienie.** Węzłami są byty, o które zadajemy pytania i które są współdzielone przez wiele innych "
  "obiektów (klient, produkt, kategoria, marka, miasto) – dzięki temu np. kategoria jest jednym węzłem, "
  "a nie tekstem powtarzanym w 125 produktach, i można od niej przechodzić do produktów i klientów. "
  "Relacjami są powiązania, po których się nawiguje: zakup, przynależność do kategorii, producent, miejsce "
  "zamieszkania i obserwowanie. Zakup jest relacją z właściwościami (ilość, data, ocena), bo opisuje "
  "konkretne zdarzenie między klientem a produktem. Właściwościami są dane opisowe niebędące punktem "
  "wyjścia do dalszych przejść (cena, wiek, nazwa, data rejestracji).")

h("4.3 Dane i import", 2)
p("Dane wygenerowano skryptem generate_data.py (Python, random.seed(42)) – są syntetyczne, więc nie "
  "podlegają zewnętrznej licencji. Każdy klient ma 1–2 ulubione kategorie (70% zakupów), co nadaje "
  "danym realistyczną strukturę i sens rekomendacjom. Pliki CSV: customers.csv (200), products.csv (125), "
  "categories.csv (8), brands.csv (12), cities.csv (8), orders.csv (1233), follows.csv (279). "
  "Graf projektu działa w osobnym kontenerze graphdb_projekt (porty 7475/7688, wolumen neo4j_projekt_data):")
code((ROOT / "projekt" / "docker-compose.yml").read_text(encoding="utf-8"))
p("Polecenia importu (plik import.cypher; wykonywane w Neo4j Browser lub skryptem projekt.py przez sterownik neo4j):")
code((ROOT / "projekt" / "import.cypher").read_text(encoding="utf-8"))
table(RP["Węzły"]); table(RP["Relacje"])
image(PSHOTS / "p_import_nodes.png", "Liczba węzłów po imporcie.", 12)
image(PSHOTS / "p_import_rels.png", "Liczba relacji po imporcie.", 12)
image(PSHOTS / "p_graph_sample.png", "Fragment grafu: zakupy klienta K072 z kategoriami i markami produktów.", 15)

h("4.4 Zapytania", 2)
p("Przygotowano 13 zapytań (7 agregacyjnych, 5 opartych na wzorcach ścieżek – w tym shortestPath i dwa "
  "ze ścieżkami o zmiennej długości). Wszystkie zapytania znajdują się w pliku queries.cypher.")
for qid, kind, req, desc, query in QUERIES:
    h(f"{qid} [{kind}; {req}]", 3)
    p(desc)
    code(query)
    df = RP[qid]
    if qid == "Q8":
        chain = df["chain"].iloc[0]
        p("Łańcuch (" + str(int(df["hops"].iloc[0])) + " kroków): " + " → ".join(chain))
    else:
        table(df, max_rows=12, font=8)
    shot = PSHOTS / f"p_{qid.lower()}.png"
    image(shot, f"Wynik zapytania {qid} w Neo4j Browser.", 15)
    if qid == "Q8":
        image(PSHOTS / "p_q8_graph.png", "Najkrótsza ścieżka FOLLOWS z K072 do K031 w widoku Graph.", 15)

h("Wizualizacja wyników projektu", 3)
image(ROOT / "projekt" / "img" / "q2_revenue_by_category.png", "Przychód wg kategorii (Q2).", 13)
image(ROOT / "projekt" / "img" / "q12_revenue_trend.png", "Kwartalny przychód (Q12); 2026 Q4 obejmuje niepełny kwartał.", 13)
p("Najwięcej przychodu dają kategorie z drogimi produktami (Sport, Dom i ogród, Elektronika), choć liczba "
  "transakcji jest zbliżona we wszystkich kategoriach. Sprzedaż kwartalna jest stabilna (ok. 85–106 tys. zł); "
  "spadek w IV kw. 2026 wynika z tego, że dane obejmują tylko część kwartału.")

h("4.5 Dlaczego model grafowy, a nie dokumentowy", 2)
p("Najważniejsze pytania tej bazy dotyczą powiązań: rekomendacje „kupili również” i collaborative filtering "
  "to przejścia klient→produkt→klient→produkt, a zasięg wpływu i łańcuchy znajomości to ścieżki o zmiennej, "
  "z góry nieznanej długości. W bazie dokumentowej wymagałoby to wielokrotnych $lookup lub $graphLookup "
  "i duplikowania danych (np. listy zakupów w dokumencie klienta i listy klientów w dokumencie produktu), "
  "a w grafie są to krótkie wzorce MATCH wykonywane przez bezpośrednie przechodzenie po relacjach. Model "
  "dokumentowy byłby lepszy tylko dla samego katalogu produktów, odczytywanego w całości.")

h("4.6 Wnioski z projektu", 2)
bullet("Wzorce ścieżek pozwoliły zbudować działające rekomendacje (Q6, Q7, Q10) w kilku linijkach Cypher, "
       "bez osobnego silnika rekomendacji.")
bullet("Właściwości na relacjach (quantity, date, rating) umożliwiają agregacje biznesowe (przychód, oceny, trend) "
       "na tych samych danych, na których działają rekomendacje.")
bullet("shortestPath i ścieżki zmiennej długości (Q8, Q9) odpowiadają na pytania praktycznie niewykonalne "
       "w modelu dokumentowym – np. łańcuch 8 kroków między dwoma klientami.")
bullet("Ograniczenia unikatowości i MERGE zapewniły brak duplikatów i powtarzalność importu.")

h("4.7 Podział pracy w zespole", 2)
table(pd.DataFrame([
    ("Patryk Kaniosz", "model grafu, generator danych, import LOAD CSV, zapytania Q1–Q13, sprawozdanie"),
    ("……………", "……………"),
    ("……………", "……………"),
], columns=["osoba", "zakres prac"]))
p("Załączniki: projekt/data/*.csv, generate_data.py, import.cypher, queries.cypher, projekt.py.", italic=True)

# =============================================================== PYTANIA
doc.add_page_break()
h("5. Odpowiedzi na pytania pomocnicze")
QA = [
    ("Jakie elementy modelu grafu własności odpowiadają kolekcji, dokumentowi i polu? Czym relacja różni się od referencji?",
     "Kolekcji odpowiada etykieta węzła (np. :Penguin), dokumentowi – węzeł, polu – właściwość węzła. Referencja "
     "w bazie dokumentowej to zwykła wartość (np. _id innego dokumentu), którą trzeba ręcznie rozwiązać zapytaniem "
     "lub $lookup, a baza nie gwarantuje jej spójności. Relacja w grafie jest pełnoprawnym elementem danych: "
     "zawsze łączy dokładnie dwa istniejące węzły, ma typ i kierunek, może mieć własne właściwości i jest "
     "przechodzona bezpośrednio (bez wyszukiwania po indeksie) – można ją dopasowywać we wzorcach."),
    ("Czy w MATCH trzeba podawać kierunek relacji? Kiedy można go pominąć?",
     "Nie trzeba. Wzorzec (a)-[:R]-(b) bez strzałki dopasowuje relacje w obu kierunkach. Kierunek można pominąć, "
     "gdy nie ma on znaczenia dla pytania (np. „czy te węzły są połączone”, relacje symetryczne w rodzaju "
     "znajomości) albo gdy typ relacji jednoznacznie wyznacza kierunek. Gdy kierunek niesie znaczenie "
     "(FOLLOWS, BOUGHT), należy go podać – zapytanie jest wtedy poprawne i wydajniejsze."),
    ("Czym MERGE różni się od CREATE i dlaczego przy Species i Island użyto MERGE? Rola ograniczeń unikatowości?",
     "CREATE zawsze tworzy nowy element, MERGE najpierw szuka dopasowania całego wzorca i tworzy go tylko, gdy "
     "go nie ma („znajdź albo utwórz”). Każdy z 344 wierszy CSV zawiera nazwę gatunku i wyspy – CREATE "
     "utworzyłoby 344 węzły Species i 344 Island, a MERGE tworzy po 3 współdzielone węzły. Ograniczenie "
     "unikatowości gwarantuje na poziomie bazy, że nie powstanie duplikat (np. przy równoległym imporcie), "
     "a dodatkowo tworzy indeks, dzięki któremu MERGE/MATCH po nazwie są szybkie."),
    ("Jak Cypher reprezentuje braki danych i jak avg traktuje null? Dlaczego Adelie: 152 vs 151?",
     "Brak danych to null; w Cypherze brak właściwości i właściwość o wartości null to to samo (węzeł po prostu "
     "jej nie przechowuje). Funkcje agregujące (avg, sum, min, max, count(wyrażenie)) pomijają null, natomiast "
     "count(p) liczy węzły. Grupa Adelie ma 152 węzły, ale jeden z nich nie ma pomiaru masy, więc avg "
     "liczona jest ze 151 wartości."),
    ("Jak działa grupowanie bez GROUP BY i jak zrealizować HAVING?",
     "Grupowanie jest niejawne: jeśli w RETURN lub WITH obok funkcji agregujących występują zwykłe wyrażenia, "
     "stają się one kluczem grupowania. Odpowiednikiem HAVING jest WITH z agregacją, a po nim WHERE na "
     "wyliczonej wartości, np. WITH i.name AS island, count(p) AS cnt WHERE cnt > 100 RETURN …"),
    ("Skąd LOAD CSV czyta pliki i do czego służą toFloat/toInteger?",
     "Z katalogu importu serwera (/var/lib/neo4j/import), do którego w docker-compose.yml zamontowano "
     "lokalny podkatalog ./data – dlatego adres to file:///penguins.csv. LOAD CSV zwraca wszystkie wartości "
     "jako tekst; toFloat i toInteger konwertują je na liczby (dla pustych pól zwracają null), aby działały "
     "porównania, sortowanie liczbowe i agregacje."),
    ("Jak Cypher i MongoDB traktują null przy sortowaniu? Konsekwencje?",
     "Cypher traktuje null jako większe od wszystkich wartości: przy ORDER BY … ASC jest na końcu, przy DESC – "
     "na początku. MongoDB traktuje null jako najmniejszą wartość, więc przy sortowaniu malejącym trafia na koniec. "
     "W praktyce zapytania „top N” w Cypherze trzeba uzupełniać o WHERE x IS NOT NULL (inaczej w wyniku pojawią "
     "się rekordy bez pomiaru), a przenosząc zapytania między systemami trzeba świadomie obsłużyć braki danych."),
    ("Czym różni się DELETE od DETACH DELETE?",
     "DELETE usuwa węzeł tylko wtedy, gdy nie ma on żadnych relacji – w przeciwnym razie zgłasza błąd (Neo4j nie "
     "dopuszcza „wiszących” relacji). DETACH DELETE najpierw usuwa wszystkie relacje węzła, a potem sam węzeł. "
     "Relacje usuwa się zwykłym DELETE."),
    ("Kiedy model grafowy jest lepszy od dokumentowego, a kiedy nie?",
     "Graf sprawdza się, gdy najważniejsze są powiązania i pytania o nie: sieci społeczne, rekomendacje, grafy "
     "wiedzy (także GraphRAG), wykrywanie oszustw, sieci transportowe, zależności – zwłaszcza dla ścieżek "
     "wielokrokowych i o zmiennej długości oraz danych typu wiele-do-wielu. Baza dokumentowa jest lepsza, gdy "
     "dane są samodzielnymi, hierarchicznymi agregatami odczytywanymi w całości (katalog produktów, profile, "
     "logi, treści CMS), gdy liczy się prosty zapis i skalowanie poziome dużych wolumenów, a zapytania rzadko "
     "przechodzą między obiektami."),
]
for i, (q_, a_) in enumerate(QA, 1):
    p(f"**{i}. {q_}**")
    p(a_)

# =============================================================== WNIOSKI
h("6. Wnioski")
bullet("Neo4j uruchomiony w Dockerze (docker compose) działa bez instalacji w systemie; wolumen zapewnia trwałość "
       "danych, a montowany katalog data pozwala importować pliki CSV klauzulą LOAD CSV.")
bullet("Zbiór Palmer Penguins w modelu grafowym dał identyczne wyniki liczbowe jak w MongoDB (Lab. 4): 344 pingwiny, "
       "152 Adelie, średnie masy 5076,02 / 3733,09 / 3700,66 g.")
bullet("Cypher jest czytelny dzięki zapisowi wzorców w formie rysunku; grupowanie jest niejawne, a HAVING "
       "realizuje WITH … WHERE.")
bullet("Braki danych trzeba obsługiwać świadomie – null jest różnie sortowany w Cypherze i MongoDB, a funkcje "
       "agregujące go pomijają.")
bullet("Przewaga grafu ujawnia się w pytaniach o powiązania: jeden wzorzec ścieżki zastępuje kilka zapytań "
       "dokumentowych; w projekcie pozwoliło to łatwo zbudować rekomendacje i analizę sieci klientów "
       "(shortestPath, ścieżki zmiennej długości).")
bullet("Sterownik neo4j dla Pythona zwraca wyniki wprost jako DataFrame (Result.to_df), co ułatwia dalszą analizę "
       "i wizualizację w pandas/Seaborn.")

out = ROOT / "Sprawozdanie_Lab5.docx"
doc.save(out)
print("zapisano", out, "rysunków:", fig_no[0])
