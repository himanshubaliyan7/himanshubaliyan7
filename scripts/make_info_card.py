#!/usr/bin/env python3
"""
Step 4 - the neofetch-style info card (info-card.svg).

Hand-authored content: edit ROWS below. Keep it to the story the contribution
graph can't tell. Each line fades and slides in on a short stagger, once.
STATIC=1 emits a frozen frame for local previews.
"""
import html
import os

from common import (BLUE, BRIGHT, CYAN, DISPLAY_NAME, FRAME, GOLD, GREEN,
                    MUTED, PINK, PROMPT, ROOT, STATIC, TEXT, window)

OUT = os.path.join(ROOT, "info-card.svg")
W, H = 980, 770          # shown at 490 x 385 in the README
PAD, SIZE, LINE = 34, 22, 37
KEY_W = 8                # characters reserved for the key column

# (key, value, key color). A None key draws a section gap.
ROWS = [
    ("Role", "Full-Stack Web Developer", CYAN),
    ("Edu", "Master's, Hindustan Institute of Technology & Science", CYAN),
    ("Status", "Open to full-time software roles", GREEN),
    (None, None, None),
    ("Now", "air-pollution-backend - Delhi NCR air-quality forecasting", GOLD),
    ("", "ingestion, models, API, Airflow (Python)", GOLD),
    ("Also", "helix-platform - API gateway + microservices", GOLD),
    ("Prev", "Phishing detection with machine learning", GOLD),
    (None, None, None),
    ("Web", "TypeScript, React, Next.js, Node.js, Express", PINK),
    ("Data", "MongoDB, PostgreSQL, MySQL", PINK),
    ("Cloud", "AWS, Azure, Docker, Kubernetes", PINK),
    ("Also", "Java / Spring, Python, TensorFlow", PINK),
    (None, None, None),
    ("Site", "himanshubaliyan.in", BLUE),
    ("Off", "sci-fi films, video games, learning guitar", BLUE),
]

SWATCHES = ["#ff5f56", GOLD, GREEN, CYAN, BLUE, PINK, TEXT, MUTED]


def render():
    p = window(W, H, f"{PROMPT}: ~$ neofetch", "ibg")
    if not STATIC:
        p.append("<style>@keyframes in{from{opacity:0;transform:translateX(-14px)}"
                 "to{opacity:1;transform:translateX(0)}}"
                 ".l{animation:in .45s ease-out both}</style>")

    step = [0]

    def line(body, y):
        anim = "" if STATIC else f' class="l" style="animation-delay:{0.35 + step[0] * 0.13:.2f}s"'
        step[0] += 1
        p.append(f'<g{anim}><text xml:space="preserve" x="{PAD}" y="{y}" font-size="{SIZE}">{body}</text></g>')

    user, host = PROMPT.split("@")
    y = 30 + 50
    line(f'<tspan fill="{CYAN}" font-weight="700">{user}</tspan><tspan fill="{MUTED}">@</tspan>'
         f'<tspan fill="{CYAN}" font-weight="700">{host}</tspan>'
         f'<tspan fill="{MUTED}">  -  {html.escape(DISPLAY_NAME)}</tspan>', y)
    y += LINE - 8
    line(f'<tspan fill="{FRAME}">{"-" * 56}</tspan>', y)
    y += LINE

    for key, value, color in ROWS:
        if key is None:
            y += LINE * 0.42
            continue
        label = (key + ":" if key else "").ljust(KEY_W)
        line(f'<tspan fill="{color}" font-weight="700">{label}</tspan>'
             f'<tspan fill="{BRIGHT if key else TEXT}">{html.escape(value)}</tspan>', y)
        y += LINE

    y += 6
    anim = "" if STATIC else f' class="l" style="animation-delay:{0.35 + step[0] * 0.13:.2f}s"'
    boxes = "".join(f'<rect x="{PAD + i * 40}" y="{y - 20}" width="34" height="24" rx="4" fill="{c}"/>'
                    for i, c in enumerate(SWATCHES))
    p.append(f"<g{anim}>{boxes}</g>")
    assert y + 10 < H, f"content overflows the card ({y} >= {H}); trim ROWS"
    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    svg = render()
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg):,} bytes)")
