#!/usr/bin/env python3
"""
Step 3a - prepare a photo for ASCII conversion. Run once per photo:

    python scripts/prep_photo.py source-photo.jpg

1. remove the background (rembg, if installed) so the subject is isolated
2. boost local contrast with CLAHE so a flat face gets highlights and shadows
3. composite onto pure white so the background maps to blank characters

Writes a grayscale source-prepped.png for make_ascii_svg.py.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

from common import ROOT

if len(sys.argv) < 2:
    sys.exit("usage: python scripts/prep_photo.py <photo> [output.png]")
SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "source-prepped.png")
ASPECT = 700 / 694  # width / height of the art area in make_ascii_svg.py

img = Image.open(SRC).convert("RGBA")
try:
    from rembg import remove
    img = remove(img)
except ImportError:
    print("rembg not installed - keeping the original background "
          "(use a photo with a plain, light background, or pip install rembg onnxruntime)")

rgb = np.array(img.convert("RGB"))
alpha = np.array(img.split()[-1]).astype(np.float32) / 255.0
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
gray = clahe.apply(gray).astype(np.float32)

mask = cv2.GaussianBlur(alpha, (0, 0), 1.2)       # feather the cut-out edge
out = (gray * mask + 255.0 * (1.0 - mask)).astype(np.uint8)

# crop to the subject, then pad with white to the ASCII grid's aspect ratio
ys, xs = np.where(alpha > 0.08)
out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
h, w = out.shape
side_w = max(w, int(round(h * ASPECT)))
side_h = max(h, int(round(side_w / ASPECT)))
canvas = np.full((side_h, side_w), 255, np.uint8)
x0 = (side_w - w) // 2
canvas[side_h - h:, x0:x0 + w] = out              # sit the subject on the bottom edge

Image.fromarray(canvas, mode="L").save(OUT)
print("wrote", OUT, canvas.shape)
