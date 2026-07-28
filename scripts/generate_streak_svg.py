#!/usr/bin/env python3
"""Generate an animated GitHub-streak SVG (squares light up one by one)."""

import sys
import json
import os
import datetime
import urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else "KULDEEPSISODIYA"
OUT = sys.argv[2] if len(sys.argv) > 2 else "streak.svg"


def get_data(user):
    url = f"https://github-contributions-api.jogruber.de/v4/{user}?y=last"
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contrib.json")
        if os.path.exists(here):
            print(f"API failed ({e}); using local contrib.json")
            return json.load(open(here))
        raise


data = get_data(USER)
contribs = data["contributions"]
total = data["total"]["lastYear"]

# ---------------- Layout ----------------
CELL = 13
GAP = 3
RAD = 2.5
LEFT = 34
TOP = 24

COLORS = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353"
]

GRAY = "#7d8590"

MONTHS = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

# ---------------- Calendar Alignment ----------------

first = datetime.date.fromisoformat(contribs[0]["date"])
last = datetime.date.fromisoformat(contribs[-1]["date"])

# GitHub contribution graph always starts on Sunday
sd = first - datetime.timedelta(days=(first.weekday() + 1) % 7)

NW = ((last - sd).days // 7) + 1

W = LEFT + NW * (CELL + GAP) + 6
H = TOP + 7 * (CELL + GAP) + 22

# ---------------- Animation ----------------

REVEAL = 3.6
DUR = 0.55
maxorder = max((NW - 1) + 6 * 0.55, 1)

rects = []
labels = []

# Month labels
last_month = None

for wk in range(NW):
    d = sd + datetime.timedelta(days=wk * 7)
    if d.month != last_month:
        last_month = d.month
        labels.append(
            f'<text class="lbl" x="{LEFT + wk*(CELL+GAP)}" y="{TOP-8}">{MONTHS[d.month-1]}</text>'
        )

# Weekday labels
for name, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
    labels.append(
        f'<text class="lbl" x="2" y="{TOP + row*(CELL+GAP) + CELL - 2}">{name}</text>'
    )

# Contribution squares
for c in contribs:

    date = datetime.date.fromisoformat(c["date"])

    week = (date - sd).days // 7
    row = (date.weekday() + 1) % 7
    level = c["level"]

    x = LEFT + week * (CELL + GAP)
    y = TOP + row * (CELL + GAP)

    delay = round(((week + row * 0.55) / maxorder) * REVEAL, 3)

    cls = "c g" if level > 0 else "c"

    rects.append(
        f'<rect class="{cls}" '
        f'x="{x}" y="{y}" '
        f'width="{CELL}" height="{CELL}" '
        f'rx="{RAD}" '
        f'fill="{COLORS[level]}" '
        f'style="animation-delay:{delay}s"/>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{W}"
height="{H}"
viewBox="0 0 {W} {H}"
font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">

<style>

text.lbl {{
    fill:{GRAY};
    font-size:13px;
    font-weight:600;
}}

text.total {{
    fill:#e6edf3;
    font-size:15px;
    font-weight:700;
}}

.c {{
    transform-box:fill-box;
    transform-origin:center;
    opacity:0;
    animation:pop {DUR}s ease-out both;
}}

.g {{
    animation:
        pop {DUR}s ease-out both,
        flash {DUR+0.15}s ease-out both;
}}

@keyframes pop {{
    0% {{
        opacity:0;
        transform:scale(.2);
    }}
    60% {{
        opacity:1;
        transform:scale(1.1);
    }}
    100% {{
        opacity:1;
        transform:scale(1);
    }}
}}

@keyframes flash {{
    0% {{
        filter:brightness(2.4);
    }}
    45% {{
        filter:brightness(2.4);
    }}
    100% {{
        filter:brightness(1);
    }}
}}

@media (prefers-reduced-motion: reduce) {{
    .c {{
        opacity:1 !important;
        animation:none !important;
    }}
}}

</style>

<rect width="{W}" height="{H}" fill="none"/>

{''.join(labels)}

{''.join(rects)}

<text class="total" x="{LEFT}" y="{H-6}">
{total:,} contributions in the last year
</text>

</svg>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"Wrote {OUT}: {len(contribs)} days, {total:,} contributions")
