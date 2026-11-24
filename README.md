# Laboratorium 5 – grafowa baza danych Neo4j

Bazy danych dla sztucznej inteligencji – *Utworzenie i zarządzanie grafową bazą danych. Realizacja zapytań.*

Sprawozdanie: [`Sprawozdanie_Lab5.docx`](Sprawozdanie_Lab5.docx)

## Zawartość

| Plik / katalog | Opis |
|---|---|
| `docker-compose.yml` | serwer Neo4j (kontener `graphdb`, porty 7474 / 7687) |
| `data/penguins.csv` | zbiór Palmer Penguins (344 obserwacje, CC0) |
| `queries_penguins.py` | wszystkie zapytania Cypher z instrukcji (ćw. 2–6) i ćwiczeń samodzielnych 1–2 |
| `wyniki_penguins.md` | pełne wyniki tych zapytań |
| `analiza.ipynb` | ćw. 7 i ćwiczenie samodzielne 3 – sterownik `neo4j`, pandas, Seaborn |
| `screenshots.py` | automatyczne zrzuty wyników z Neo4j Browser (Playwright + Edge) |
| `build_report.py` | generator sprawozdania `.docx` |
| `projekt/` | projekt zespołowy: **graf zakupowy z rekomendacjami** (kontener `graphdb_projekt`, porty 7475 / 7688) |

### Projekt (`projekt/`)

- `generate_data.py` – generator danych syntetycznych (seed 42) → `data/*.csv`
- `import.cypher` – import `LOAD CSV` z ograniczeniami unikatowości
- `queries.cypher` – 13 zapytań (agregacje, rekomendacje, `shortestPath`, ścieżki zmiennej długości)
- `projekt.py` – import i zapytania przez sterownik `neo4j`, wyniki w `wyniki_projekt.md`
- `img/model.png` – model grafu

Węzły: `Customer` (200), `Product` (125), `Category`, `Brand`, `City`;
relacje: `BOUGHT {quantity, date, rating}`, `BELONGS_TO`, `MADE_BY`, `LIVES_IN`, `FOLLOWS`.

## Uruchomienie

```bash
docker compose up -d                              # graf penguins
docker compose -f projekt/docker-compose.yml up -d  # graf projektu
uv sync
uv run queries_penguins.py          # import + zapytania penguins
uv run projekt/projekt.py           # import + zapytania projektu
uv run jupyter nbconvert --to notebook --execute --inplace analiza.ipynb
uv run screenshots.py && uv run screenshots.py projekt
uv run build_report.py              # Sprawozdanie_Lab5.docx
```
