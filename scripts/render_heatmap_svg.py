#!/usr/bin/env python3
"""
Step 5b - draw data/contributions.json as contrib-heatmap.svg.

The classic 53-week x 7-day calendar of rounded boxes. Boxes slide in on a
diagonal sweep (CSS keyframes inside the SVG: plays once on load, then holds),
followed by a Less -> More legend and a stats footer.
"""
import datetime
import json
import os

from common import (BRIGHT, CYAN, FRAME, GOLD, GREEN, MUTED, PROMPT, ROOT,
                    STATIC, window)

IN = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end, used for the best day)

CELL, GAP = 12, 3
STEP = CELL + GAP
PAD, LABEL_W, MONTH_H, BAR_H, FOOTER_H = 22, 30, 20, 30, 86
COL_T, ROW_T, CELL_DUR = 0.018, 0.045, 0.42   # reveal timing


def columns(days):
    """Group days into Sunday-first week columns; None pads partial weeks."""
    cols, col = [], []
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        if weekday == 0 and col:
            cols.append(col + [None] * (7 - len(col)))
            col = []
        col += [None] * (weekday - len(col))
        col.append((date, d["count"], d["level"]))
    if col:
        cols.append(col + [None] * (7 - len(col)))
    return cols


def plural(n, word):
    return f"{n:,} {word}" + ("" if n == 1 else "s")


def render(data):
    cols = columns(data["days"])
    best = data["best_day"]
    width = PAD + LABEL_W + len(cols) * STEP - GAP + PAD
    left, top = PAD + LABEL_W, BAR_H + 10 + MONTH_H
    grid_h = 7 * STEP - GAP
    height = top + grid_h + FOOTER_H + 26

    p = window(width, height, f"{PROMPT}: ~/contributions --graph", "hbg")
    if not STATIC:
        p.append("<style>@keyframes drop{from{opacity:0;transform:translateY(-7px)}"
                 "to{opacity:1;transform:translateY(0)}}"
                 f".c{{animation:drop {CELL_DUR}s cubic-bezier(.2,.8,.2,1) both}}</style>")

    last_label = -4
    for ci, col in enumerate(cols):
        first = next(c for c in col if c)[0]
        month_start = any(c and c[0].day == 1 for c in col) or ci == 0
        if month_start and ci - last_label >= 3 and ci < len(cols) - 1:
            label = max((c[0] for c in col if c)).strftime("%b") if ci else first.strftime("%b")
            p.append(f'<text x="{left + ci * STEP}" y="{top - 8}" fill="{MUTED}" font-size="10">{label}</text>')
            last_label = ci
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        p.append(f'<text x="{PAD}" y="{top + row * STEP + 10}" fill="{MUTED}" font-size="9">{name}</text>')

    for ci, col in enumerate(cols):
        for ri, cell in enumerate(col):
            if not cell:
                continue
            date, count, level = cell
            if count and count == best["count"]:
                level = 5
            anim = "" if STATIC else f' class="c" style="animation-delay:{ci * COL_T + ri * ROW_T:.3f}s"'
            p.append(f'<rect{anim} x="{left + ci * STEP}" y="{top + ri * STEP}" width="{CELL}" '
                     f'height="{CELL}" rx="2.5" fill="{PALETTE[min(level, 5)]}" stroke="#ffffff" stroke-opacity="0.05">'
                     f'<title>{date}: {plural(count, "contribution")}</title></rect>')

    ly = top + grid_h + 10
    lx = width - PAD - 30 - len(PALETTE) * (CELL + 2)
    p.append(f'<text x="{lx - 6}" y="{ly + 10}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    for i, color in enumerate(PALETTE):
        p.append(f'<rect x="{lx + i * (CELL + 2)}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
    p.append(f'<text x="{width - PAD}" y="{ly + 10}" fill="{MUTED}" font-size="10" text-anchor="end">More</text>')

    sep = ly + CELL + 14
    p.append(f'<line x1="0" y1="{sep}" x2="{width}" y2="{sep}" stroke="{FRAME}"/>')
    y1, y2 = sep + 26, sep + 50
    rng, cur, lon = data["range"], data["current_streak"], data["longest_streak"]
    p.append(f'<text x="{PAD}" y="{y1}" font-size="13" fill="{MUTED}">'
             f'<tspan fill="{GREEN}" font-weight="700">{data["total_contributions"]:,}</tspan>'
             f' contributions in the last year</text>')
    p.append(f'<text x="{width - PAD}" y="{y1}" font-size="12" fill="{MUTED}" text-anchor="end">'
             f'{rng["start"]} &#8594; {rng["end"]}</text>')
    p.append(f'<text x="{PAD}" y="{y2}" font-size="13" fill="{MUTED}">current streak '
             f'<tspan fill="{CYAN}" font-weight="700">{plural(cur["length"], "day")}</tspan>'
             f'   &#183;   longest <tspan fill="{CYAN}" font-weight="700">{plural(lon["length"], "day")}</tspan>'
             f'   &#183;   <tspan fill="{BRIGHT}">{plural(data["active_days"], "active day")}</tspan></text>')
    p.append(f'<text x="{width - PAD}" y="{y2}" font-size="12" fill="{MUTED}" text-anchor="end">best day '
             f'<tspan fill="{GOLD}" font-weight="700">{best["count"]}</tspan> on {best["date"]}</text>')
    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    with open(IN) as f:
        svg = render(json.load(f))
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg):,} bytes)")
