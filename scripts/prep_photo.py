#!/usr/bin/env python3
"""
Step 3a - prepare a photo for ASCII conversion. Run once per photo:

    python scripts/prep_photo.py source-photo.jpg

1. remove the background (rembg, if installed) so the subject is isolated.
   A PNG that already has a transparent background is used as-is.
2. boost local contrast with CLAHE so a flat face gets highlights and shadows
3. trace the silhouette, so light clothing doesn't vanish into the background
4. composite onto pure white so the background maps to blank characters

Writes a grayscale source-prepped.png for make_ascii_svg.py.

KEEP=0.45 (env) keeps the top 45% of the subject - head and shoulders read
better than a full torso at ASCII resolution. KEEP=1 keeps everything.
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
KEEP = float(os.environ.get("KEEP", 0.45))
HIGHLIGHT = float(os.environ.get("HIGHLIGHT", 70))  # percentile mapped to white
OUTLINE = 105       # gray level of the silhouette line (0 = black)

img = Image.open(SRC).convert("RGBA")
if img.getextrema()[3][0] == 255:  # fully opaque -> needs a cut-out
    try:
        from rembg import new_session, remove
        img = remove(img, session=new_session("u2net_human_seg"), post_process_mask=True)
    except ImportError:
        print("rembg not installed - keeping the original background "
              "(use a photo with a plain, light background, or pip install rembg onnxruntime)")

rgb = np.array(img.convert("RGB"))
alpha = np.array(img.split()[-1])
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

# crop to the subject (top KEEP of it) before any filtering
ys, xs = np.where(alpha > 20)
y0, y1 = ys.min(), ys.min() + int((ys.max() - ys.min() + 1) * KEEP)
band = alpha[y0:y1] > 20
x0, x1 = np.where(band.any(axis=0))[0][[0, -1]]
gray, alpha = gray[y0:y1, x0:x1 + 1], alpha[y0:y1, x0:x1 + 1]

clahe = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8))
gray = clahe.apply(gray).astype(np.float32)

# stretch tones over the subject so skin and light clothing land near white
# and only hair, beard, glasses and shadows stay dark
lo, hi = np.percentile(gray[alpha > 128], [2, HIGHLIGHT])
gray = np.clip((gray - lo) / max(hi - lo, 1.0), 0, 1) * 255.0

solid = (alpha > 128).astype(np.uint8)
if solid.min() == 0:  # there is a cut-out edge to trace
    k = max(3, int(round(max(gray.shape) * 0.007)) | 1)
    edge = cv2.morphologyEx(solid, cv2.MORPH_GRADIENT, np.ones((k, k), np.uint8))
    gray = np.where(edge > 0, np.minimum(gray, OUTLINE), gray)
    solid = cv2.dilate(solid, np.ones((k, k), np.uint8))

mask = cv2.GaussianBlur(solid.astype(np.float32), (0, 0), 1.2)
out = (gray * mask + 255.0 * (1.0 - mask)).astype(np.uint8)

# pad with white to the ASCII grid's aspect ratio, subject on the bottom edge
h, w = out.shape
side_w = max(w, int(round(h * ASPECT)))
side_h = max(h, int(round(side_w / ASPECT)))
canvas = np.full((side_h, side_w), 255, np.uint8)
left = (side_w - w) // 2
canvas[side_h - h:, left:left + w] = out

Image.fromarray(canvas, mode="L").save(OUT)
print("wrote", OUT, canvas.shape)
