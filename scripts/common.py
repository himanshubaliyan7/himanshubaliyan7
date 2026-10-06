"""Shared settings for the profile-art scripts. Edit these once."""
import os

USERNAME = os.environ.get("GH_PROFILE_USER", "himanshubaliyan7")
DISPLAY_NAME = "Himanshu Baliyan"
PROMPT = "himanshu@github"

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# terminal palette (GitHub dark)
BG_TOP = "#111722"
BG_BOTTOM = "#0d1117"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#c9d1d9"
BRIGHT = "#e6edf3"
CYAN = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"
PINK = "#f778ba"
BLUE = "#58a6ff"

STATIC = bool(os.environ.get("STATIC"))  # STATIC=1 -> frozen frame, no animation


def window(width, height, title, grad_id="bg"):
    """Opening <svg> tag plus a terminal window frame with a title bar."""
    bar = 30
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT}">',
        f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/>'
        f'</linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="12" fill="url(#{grad_id})"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{bar}" x2="{width}" y2="{bar}" stroke="{FRAME}"/>',
    ]
    for i, dot in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append(f'<circle cx="{20 + i * 16}" cy="{bar / 2}" r="5" fill="{dot}"/>')
    out.append(f'<text x="{width / 2}" y="{bar / 2 + 4}" fill="{MUTED}" font-size="12" '
               f'text-anchor="middle">{title}</text>')
    return out
