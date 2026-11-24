"""Rysuje poglądowy model grafu projektu (etykiety, relacje z kierunkami, właściwości)."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

NODES = {  # nazwa: (x, y, kolor, właściwości)
    "Customer": (0.0, 0.0, "#f4a6b7", "customer_id (UNIQUE)\nname, age\nregistered: date"),
    "Product": (5.0, 0.0, "#d4a6f4", "product_id (UNIQUE)\nname\nprice: float"),
    "Category": (9.0, 2.2, "#c9a96b", "category_id (UNIQUE)\nname"),
    "Brand": (9.0, -2.2, "#8fd8ea", "brand_id (UNIQUE)\nname"),
    "City": (0.0, -3.8, "#8fdcae", "name (UNIQUE)\nvoivodeship"),
}
EDGES = [  # (od, do, typ, właściwości, rad)
    ("Customer", "Product", "BOUGHT", "{quantity, date, rating}", 0.0),
    ("Product", "Category", "BELONGS_TO", "", 0.0),
    ("Product", "Brand", "MADE_BY", "", 0.0),
    ("Customer", "City", "LIVES_IN", "", 0.0),
]

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(-3, 12); ax.set_ylim(-6, 4.5); ax.axis("off")
W, H = 2.6, 1.6
for name, (x, y, col, props) in NODES.items():
    ax.add_patch(FancyBboxPatch((x - W / 2, y - H / 2), W, H, boxstyle="round,pad=0.08,rounding_size=0.4",
                                fc=col, ec="#333", lw=1.2, zorder=2))
    ax.text(x, y + 0.45, f":{name}", ha="center", va="center", fontsize=12, weight="bold", zorder=3)
    ax.text(x, y - 0.2, props, ha="center", va="center", fontsize=8.5, zorder=3, linespacing=1.3)


def border(x, y, dx, dy):
    """Punkt na krawędzi prostokąta węzła (x, y) w kierunku (dx, dy)."""
    hw, hh = W / 2 + 0.12, H / 2 + 0.12
    t = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
    return x + dx * t, y + dy * t


def edge(a, b, label, props):
    (x1, y1, *_), (x2, y2, *_) = NODES[a], NODES[b]
    dx, dy = x2 - x1, y2 - y1
    p1, p2 = border(x1, y1, dx, dy), border(x2, y2, -dx, -dy)
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=18, lw=1.4,
                                 color="#444", shrinkA=0, shrinkB=0, zorder=1))
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    vertical = abs(dx) < 1e-6
    ha = "left" if vertical else "center"
    ox = 0.15 if vertical else 0
    oy = 0 if vertical else 0.25
    if not vertical and abs(dy) > 1e-6:  # skośna strzałka – etykieta obok, nie na linii
        ox, oy, ha = -0.25, (0.45 if dy > 0 else -0.45), "right"
    ax.text(mx + ox, my + oy, label, ha=ha, va="center", fontsize=10,
            weight="bold", color="#1f4e79")
    if props:
        ax.text(mx, my - 0.3, props, ha="center", va="center", fontsize=8.5, color="#555", style="italic")


for a, b, lab, pr, _ in EDGES:
    edge(a, b, lab, pr)

# pętla FOLLOWS (Customer -> Customer)
x, y = NODES["Customer"][:2]
ax.add_patch(FancyArrowPatch((x - 0.6, y + 0.85), (x + 0.6, y + 0.85), connectionstyle="arc3,rad=-1.4",
                             arrowstyle="-|>", mutation_scale=18, lw=1.4, color="#444"))
ax.text(x, y + 2.35, "FOLLOWS", ha="center", fontsize=10, weight="bold", color="#1f4e79")
ax.set_title("Model grafu: sklep internetowy z rekomendacjami", fontsize=14, weight="bold")
out = Path(__file__).parent / "img" / "model.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(out)
