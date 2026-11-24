"""Generuje notatnik analiza.ipynb (Ćw. 7 z instrukcji + ćwiczenie samodzielne nr 3)."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md("# Laboratorium 5 – Neo4j w Pythonie\n\n"
       "Ćwiczenie nr 7 (instrukcja) oraz ćwiczenie samodzielne nr 3."),
    md("## Połączenie z serwerem Neo4j (protokół Bolt, port 7687)"),
    code('from neo4j import GraphDatabase, Result\n\n'
         'driver = GraphDatabase.driver(\n    "bolt://localhost:7687", auth=None\n)\n'
         'driver.verify_connectivity()\nprint("Połączono z Neo4j")'),
    md("## Ćw. 7.3 – wynik zapytania jako DataFrame"),
    code('query = """\nMATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)\nRETURN s.name AS species,\n'
         '       round(avg(p.body_mass_g), 2) AS avg_mass,\n       count(p) AS cnt\n'
         'ORDER BY avg_mass DESC\n"""\n'
         'df = driver.execute_query(\n    query, result_transformer_=Result.to_df\n)\nprint(df)'),
    md("## Ćw. 7.4 – wykres średniej masy ciała"),
    code('import seaborn as sns\nimport matplotlib.pyplot as plt\n\n'
         'sns.barplot(data=df, x="species", y="avg_mass")\n'
         'plt.xlabel("Gatunek")\nplt.ylabel("Średnia masa ciała [g]")\n'
         'plt.title("Średnia masa ciała według gatunku")\n'
         'plt.savefig("img/cw7_avg_mass.png", dpi=150, bbox_inches="tight")\nplt.show()'),
    md("## Ćwiczenie samodzielne nr 3 – długość płetwy wg gatunku i płci\n\n"
       "Wybrano zapytanie agregacyjne z ćwiczenia samodzielnego 2 (2): średnia, minimalna "
       "i maksymalna długość płetwy dla par gatunek–płeć (bez węzłów z brakiem płci)."),
    code('query_flipper = """\nMATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)\nWHERE p.sex IS NOT NULL\n'
         'RETURN s.name AS species, p.sex AS sex,\n'
         '       round(avg(p.flipper_length_mm), 2) AS avg_flipper,\n'
         '       min(p.flipper_length_mm) AS min_flipper,\n'
         '       max(p.flipper_length_mm) AS max_flipper,\n'
         '       count(p) AS cnt\nORDER BY species, sex\n"""\n'
         'df_f = driver.execute_query(query_flipper, result_transformer_=Result.to_df)\ndf_f'),
    code('import numpy as np\n\n'
         'sns.set_theme(style="whitegrid")\n'
         'fig, ax = plt.subplots(figsize=(8, 5))\n'
         'sns.barplot(data=df_f, x="species", y="avg_flipper", hue="sex",\n'
         '            palette={"female": "#d6604d", "male": "#4393c3"}, ax=ax)\n'
         '# zakres min–max jako "wąsy" nad słupkami\n'
         'n_hue = df_f["sex"].nunique()\n'
         'for bar_container, sex in zip(ax.containers, ["female", "male"]):\n'
         '    sub = df_f[df_f["sex"] == sex].set_index("species").loc[[t.get_text() for t in ax.get_xticklabels()]]\n'
         '    for bar, (_, row) in zip(bar_container, sub.iterrows()):\n'
         '        x = bar.get_x() + bar.get_width() / 2\n'
         '        ax.errorbar(x, row.avg_flipper,\n'
         '                    yerr=[[row.avg_flipper - row.min_flipper], [row.max_flipper - row.avg_flipper]],\n'
         '                    fmt="none", ecolor="black", capsize=4, lw=1)\n'
         '    ax.bar_label(bar_container, fmt="%.1f", label_type="center", color="white", fontsize=9)\n'
         'ax.set_ylim(150, 240)\n'
         'ax.set_xlabel("Gatunek")\nax.set_ylabel("Długość płetwy [mm]")\n'
         'ax.set_title("Średnia długość płetwy wg gatunku i płci (wąsy: min–max)")\n'
         'ax.legend(title="Płeć", labels=None)\n'
         'plt.savefig("img/samodz3_flipper.png", dpi=150, bbox_inches="tight")\nplt.show()'),
    md("**Interpretacja.** Gentoo ma wyraźnie najdłuższe płetwy (średnio ok. 213 mm u samic "
       "i 222 mm u samców), o ponad 20 mm więcej niż Adelie i Chinstrap, których zakresy "
       "w dużej mierze się pokrywają. W każdym gatunku samce mają dłuższe płetwy od samic "
       "(różnica ok. 5–9 mm), co potwierdza dymorfizm płciowy. Długość płetwy jest więc dobrą "
       "cechą do odróżnienia Gentoo od pozostałych gatunków, ale słabo rozdziela Adelie i Chinstrap."),
    md("## Dodatkowo – trend średniej masy w latach (ćw. samodzielne 2 (3))"),
    code('query_year = """\nMATCH (p:Penguin)-[:OF_SPECIES]->(s:Species)\n'
         'RETURN s.name AS species, p.year AS year,\n       round(avg(p.body_mass_g), 2) AS avg_mass\n'
         'ORDER BY species, year\n"""\n'
         'df_y = driver.execute_query(query_year, result_transformer_=Result.to_df)\n'
         'fig, ax = plt.subplots(figsize=(7, 4))\n'
         'sns.lineplot(data=df_y, x="year", y="avg_mass", hue="species", marker="o", ax=ax)\n'
         'ax.set_xticks([2007, 2008, 2009])\n'
         'ax.set_xlabel("Rok obserwacji")\nax.set_ylabel("Średnia masa ciała [g]")\n'
         'ax.set_title("Średnia masa ciała wg roku i gatunku")\n'
         'plt.savefig("img/samodz2_trend.png", dpi=150, bbox_inches="tight")\nplt.show()'),
    code("driver.close()"),
]
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3 (.venv)", "language": "python"}
nbf.write(nb, "analiza.ipynb")
