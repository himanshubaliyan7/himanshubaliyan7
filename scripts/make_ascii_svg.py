#!/usr/bin/env python3
"""
Step 3b - turn source-prepped.png into a self-typing ASCII portrait SVG.

The image is downsampled to a character grid and each pixel's brightness picks
a glyph from a density ramp. One light-gray ink color, high contrast. Each row
is clipped by a rectangle that wipes left to right (a block cursor rides the
edge), staggered top to bottom; the portrait prints once and holds. It is all
SMIL inside the SVG, so GitHub plays it.

Until you add a photo (see prep_photo.py) it draws a monogram placeholder.
"""
import html
import os
import sys

from PIL import Image, ImageDraw, ImageFont

from common import DISPLAY_NAME, FRAME, MUTED, PROMPT, ROOT, STATIC, TEXT, window

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source-prepped.png")
OUT = os.path.join(ROOT, "portrait-ascii.svg")

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); leading space clears the background
COLS, ROWS = 100, 53
W, H = 740, 770          # shown at 370 x 385 in the README
PAD, BAR_H, STATUS_H = 20, 30, 30
ART_W = W - 2 * PAD
ART_TOP = BAR_H + 8
CELL_W = ART_W / COLS
CELL_H = (H - BAR_H - STATUS_H - 16) / ROWS
GAMMA = 1.15             # > 1 brightens midtones so a face lands in sparser glyphs
WHITE_FLOOR = 0.82       # anything brighter is forced blank
TOTAL = 5.5              # seconds for the whole portrait to print


def placeholder():
    """Initials in a ring, used until a real photo is supplied."""
    size = 600
    img = Image.new("L", (size, size), 255)
    draw = ImageDraw.Draw(img)
    draw.ellipse((40, 40, size - 40, size - 40), outline=110, width=26)
    initials = "".join(w[0] for w in DISPLAY_NAME.split()[:2]).upper()
    font = None
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "C:/Windows/Fonts/arialbd.ttf"):
        if os.path.exists(path):
            font = ImageFont.truetype(path, 250)
            break
    font = font or ImageFont.load_default(250)
    box = draw.textbbox((0, 0), initials, font=font)
    draw.text(((size - box[2] - box[0]) / 2, (size - box[3] - box[1]) / 2), initials, fill=0, font=font)
    return img


def to_rows(img):
    px = img.convert("L").resize((COLS, ROWS), Image.LANCZOS).load()
    rows = []
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            lum = (px[x, y] / 255.0) ** (1 / GAMMA)
            if lum >= WHITE_FLOOR:
                line.append(" ")
            else:
                line.append(RAMP[min(len(RAMP) - 1, round((1 - lum) * (len(RAMP) - 1)))])
        rows.append("".join(line).rstrip())
    return rows


def render(rows):
    p = window(W, H, f"{PROMPT}: ~$ ./portrait.sh")
    row_dur = TOTAL / ROWS
    size = CELL_H * 0.9
    for i, line in enumerate(rows):
        if not line:
            continue
        top = ART_TOP + i * CELL_H
        text = (f'<text xml:space="preserve" x="{PAD}" y="{top + CELL_H * 0.78:.1f}" fill="{TEXT}" '
                f'font-size="{size:.1f}" textLength="{len(line) * CELL_W:.1f}" '
                f'lengthAdjust="spacingAndGlyphs">{html.escape(line)}</text>')
        if STATIC:
            p.append(text)
            continue
        begin = i * row_dur
        p.append(f'<clipPath id="r{i}"><rect x="{PAD}" y="{top:.1f}" width="0" height="{CELL_H + 1:.1f}">'
                 f'<animate attributeName="width" from="0" to="{ART_W}" begin="{begin:.3f}s" '
                 f'dur="{row_dur:.3f}s" fill="freeze"/></rect></clipPath>'
                 f'<g clip-path="url(#r{i})">{text}</g>'
                 f'<rect y="{top + 1:.1f}" width="{CELL_W:.1f}" height="{CELL_H - 2:.1f}" fill="{TEXT}" opacity="0">'
                 f'<animate attributeName="x" from="{PAD}" to="{PAD + ART_W}" begin="{begin:.3f}s" '
                 f'dur="{row_dur:.3f}s" fill="freeze"/>'
                 f'<set attributeName="opacity" to="0.85" begin="{begin:.3f}s"/>'
                 f'<set attributeName="opacity" to="0" begin="{begin + row_dur:.3f}s"/></rect>')

    sy = H - STATUS_H
    prompt = f"{PROMPT}:~$ whoami "
    p.append(f'<line x1="0" y1="{sy}" x2="{W}" y2="{sy}" stroke="{FRAME}"/>')
    p.append(f'<text xml:space="preserve" x="{PAD}" y="{sy + 20}" fill="{MUTED}" font-size="13">'
             f'{prompt}<tspan fill="{TEXT}">{html.escape(DISPLAY_NAME)}</tspan></text>')
    cx = PAD + (len(prompt) + len(DISPLAY_NAME) + 1) * 13 * 0.6
    blink = "" if STATIC else ('<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
                               'dur="1s" repeatCount="indefinite"/>')
    p.append(f'<rect x="{cx:.1f}" y="{sy + 8}" width="8" height="14" fill="{TEXT}">{blink}</rect>')
    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    if os.path.exists(SRC):
        image = Image.open(SRC)
    else:
        print(f"{SRC} not found - drawing the monogram placeholder")
        image = placeholder()
    svg = render(to_rows(image))
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg):,} bytes)")
