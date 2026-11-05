#!/usr/bin/env python3
"""Generate print-ready business card artwork for Huffman Writes.

Two faces, US standard 3.5 x 2.0 in (252 x 144 pt) at trim, with 1/8 in (9 pt)
bleed on every edge, so the document box is 270 x 162 pt and trim starts at 9,9.

Text is converted to outlines with fontTools, so the SVG and PDF carry no font
dependency: what you see is what the press plates get. Colors are the locked
site palette (midnight navy #131E39, amber #D4820A, Parian cream #F2EDD8).

    python3 print/business-cards/make-cards.py

Writes card-front.svg, card-back.svg into this directory, then renders PDFs and
300 dpi proofs if inkscape/rsvg-convert/gs are on PATH.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = Path(__file__).resolve().parent
FONT_DIR = HERE / "fonts"
OUT = HERE

# ---------------------------------------------------------------- geometry ---
IN = 72.0
BLEED = 9.0                     # 1/8 in
CARD_W, CARD_H = 3.5 * IN, 2.0 * IN      # 252 x 144
DOC_W, DOC_H = CARD_W + 2 * BLEED, CARD_H + 2 * BLEED   # 270 x 162
TRIM_L, TRIM_T = BLEED, BLEED
TRIM_R, TRIM_B = BLEED + CARD_W, BLEED + CARD_H
SAFE = 9.0                      # 1/8 in inside trim
LEFT = TRIM_L + SAFE + 9        # optical margin: 27 pt
RIGHT = TRIM_R - SAFE - 9       # 243

# ------------------------------------------------------------------ color ---
# INK is NOT the site's ink. The site runs midnight navy #131E39 (see
# assets/css/ and hugo.toml); Philip read that as blue on the first proof
# (2026-11-05) and asked for it removed, so both faces are warm near-black on
# Parian ivory. That divergence is a decision, not drift: do not "harmonize" the
# card back to navy, and do not move the site to INK, without asking him.
# Amber and ivory are untouched from the locked palette.
INK = "#1A1714"
AMBER = "#D4820A"
CREAM = "#F2EDD8"

NAME = "PHILIP R. HUFFMAN"
PHONE = "(816) 204-1916"
ROLE = "WRITER"
CREDO = "Think clearly. Live intentionally. Love deeply."
DOMAIN = "www.huffmanwrites.org"
EMAIL = "phil@huffmanwrites.org"
BLUESKY = "@huffmanwrites"
FOOTER = "ESSAYS · BOOKS · WEEKLY DIGEST"

# Scan payload: MECARD is the compact contact form iOS and Android both offer
# to save straight into Contacts. Kept short enough to stay at QR version 5 so
# each module prints at 0.5 mm on a 0.8 in square.
MECARD = ("MECARD:N:Huffman,Philip R.;TEL:+18162041916;"
          "EMAIL:phil@huffmanwrites.org;URL:huffmanwrites.org;;")

MONOGRAM_SVG = HERE / "prh-monogram.svg"

sys.path.insert(0, str(HERE / "vendor"))
import qrcode  # noqa: E402  (vendored in vendor/qrcode)
import qrcode.constants as QR_C  # noqa: E402


# ------------------------------------------------------------------- fonts ---
_cache: dict[tuple[str, int], tuple[TTFont, dict]] = {}


def font(family: str, weight: int) -> tuple[TTFont, dict]:
    key = (family, weight)
    if key in _cache:
        return _cache[key]

    path = FONT_DIR / f"{family}.ttf"
    f = TTFont(path)
    axes = {a.axisTag: a.defaultValue for a in f["fvar"].axes} if "fvar" in f else {}
    if "wght" in axes:
        axes["wght"] = weight
    if "opsz" in axes:
        axes["opsz"] = 14
    if axes:
        f = instantiateVariableFont(f, axes, inplace=False)
    gs = f.getGlyphSet()
    _cache[key] = (f, gs)
    return f, gs


def _advance(f: TTFont, gs, name: str) -> float:
    return f["hmtx"][name][0] / f["head"].unitsPerEm


def text_width(family: str, weight: int, size: float, text: str, tracking: float = 0.0) -> float:
    f, gs = font(family, weight)
    cmap = f.getBestCmap()
    total = 0.0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        total += _advance(f, gs, name) * size
    return total + tracking * max(len(text) - 1, 0)


def text_path(family: str, weight: int, size: float, text: str,
              x: float, y: float, tracking: float = 0.0,
              anchor: str = "start") -> str:
    """Return an SVG path 'd' for `text` with its baseline at y.

    anchor: start | middle | end, measured on the advance width.
    """
    f, gs = font(family, weight)
    cmap = f.getBestCmap()
    s = size / f["head"].unitsPerEm
    width = text_width(family, weight, size, text, tracking)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width

    parts: list[str] = []
    pen_x = x
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        pen = SVGPathPen(gs)
        gs[name].draw(pen)
        d = pen.getCommands()
        if d:
            # glyph coords are y-up font units; flip and scale into place
            parts.append(f'<path transform="translate({pen_x:.3f} {y:.3f}) '
                         f'scale({s:.6f} {-s:.6f})" d="{d}"/>')
        pen_x += _advance(f, gs, name) * size + tracking
    return "".join(parts)


# ---------------------------------------------------------------- monogram ---
def monogram_art() -> tuple[str, str, float]:
    """Traced monogram: (path_d, inner_transform, art_board_edge).

    potrace emits `<g transform="translate(0,H) scale(s,-s)">`, which flips its
    y-up coordinate frame into an upright art board one SVG-width unit wide.
    Keeping that
    transform nested means the caller only has to scale, never re-derive the
    flip, and a re-trace at any resolution drops in without touching this file.
    """
    src = MONOGRAM_SVG.read_text()
    paths = re.findall(r'<path[^>]*\sd="([^"]+)"', src, re.S)
    d = " ".join(p.replace("\n", " ") for p in paths)
    tr = re.search(r'transform="([^"]+)"', src).group(1)
    w = float(re.search(r'\swidth="([\d.]+)pt"', src).group(1))
    return d, tr, w


def monogram(art: tuple[str, str, float], x: float, y: float,
             height: float, fill: str) -> str:
    """Place the art board with its top-left corner at x,y and `height` pt tall."""
    d, tr, board = art
    k = height / board
    return (f'<g transform="translate({x:.3f} {y:.3f}) scale({k:.6f})" fill="{fill}">'
            f'<g transform="{tr}"><path d="{d}"/></g></g>')


# ---------------------------------------------------------------------- qr ---
def qr_path(data: str, x: float, y: float, size: float,
            ec: str = "M") -> tuple[str, int, float]:
    """Return (path_d, module_count, module_size_pt) for `data`.

    The matrix is drawn module-per-module as one path, so the code is vector on
    the plate: no resampling, no soft edges at the scanner's threshold.
    """
    q = qrcode.QRCode(error_correction=getattr(QR_C, f"ERROR_CORRECT_{ec}"), border=0)
    q.add_data(data)
    q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    u = size / n
    d = []
    for row, bits in enumerate(m):
        for col, dark in enumerate(bits):
            if dark:
                d.append(f"M{x + col * u:.3f} {y + row * u:.3f}h{u:.3f}v{u:.3f}h-{u:.3f}z")
    return "".join(d), n, u


# ------------------------------------------------------------------- faces ---
def front(art) -> str:
    mon_h = 26.0
    mon_w = mon_h  # square art board
    cx = DOC_W / 2

    name_y = 96.0
    rule_y = 105.0
    credo_y = 122.0

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{DOC_W}pt" height="{DOC_H}pt" '
        f'viewBox="0 0 {DOC_W} {DOC_H}">',
        "<title>Huffman Writes — business card, front</title>",
        "<desc>3.5 × 2.0 in trim, 0.125 in bleed, Parian ivory field, warm-black type, "
        "amber rule and frame.</desc>",
        f'<rect x="0" y="0" width="{DOC_W}" height="{DOC_H}" fill="{CREAM}"/>',
        # amber hairline frame, 7 pt inside trim
        f'<rect x="{TRIM_L + 7}" y="{TRIM_T + 7}" width="{CARD_W - 14}" height="{CARD_H - 14}" '
        f'fill="none" stroke="{AMBER}" stroke-opacity="0.5" stroke-width="0.5"/>',
        monogram(art, cx - mon_w / 2, 38.0, mon_h, INK),
        f'<g fill="{INK}">',
        text_path("CrimsonPro", 600, 13.0, NAME, cx, name_y, tracking=2.1, anchor="middle"),
        "</g>",
        f'<rect x="{cx - 10}" y="{rule_y}" width="20" height="0.7" fill="{AMBER}"/>',
        f'<g fill="{INK}" fill-opacity="0.82">',
        text_path("CrimsonPro-Italic", 400, 9.0, CREDO, cx, credo_y, tracking=0.25, anchor="middle"),
        "</g>",
        "</svg>",
    ]
    return "\n".join(out)


def back(art) -> str:
    header_y = 40.0
    role_y = 49.0
    rule_y = 56.0
    rows = [("PHONE", PHONE), ("EMAIL", EMAIL), ("WEB", DOMAIN), ("BLUESKY", BLUESKY)]
    first_y = 78.0
    step = 16.0

    qr_size = 0.80 * IN                    # 57.6 pt square
    qr_x = RIGHT - qr_size                 # right edge on the safe margin
    qr_y = TRIM_B - SAFE - qr_size         # bottom edge on the safe margin
    qr_d, qr_n, qr_u = qr_path(MECARD, qr_x, qr_y, qr_size)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{DOC_W}pt" height="{DOC_H}pt" '
        f'viewBox="0 0 {DOC_W} {DOC_H}">',
        "<title>Huffman Writes — business card, back</title>",
        "<desc>3.5 × 2.0 in trim, 0.125 in bleed, Parian ivory field, warm-black type, "
        f"MECARD QR {qr_n} modules at {qr_u:.2f} pt.</desc>",
        f'<rect x="0" y="0" width="{DOC_W}" height="{DOC_H}" fill="{CREAM}"/>',
        f'<g fill="{INK}" fill-opacity="0.82">',
        text_path("Inter", 600, 5.4, NAME, LEFT, header_y, tracking=1.25),
        "</g>",
        f'<g fill="{AMBER}">',
        text_path("Inter", 600, 5.0, ROLE, LEFT, role_y, tracking=2.0),
        "</g>",
        f'<rect x="{LEFT}" y="{rule_y}" width="12" height="0.7" fill="{AMBER}"/>',
    ]

    for i, (label, value) in enumerate(rows):
        y = first_y + i * step
        out.append(f'<g fill="{AMBER}">')
        out.append(text_path("Inter", 600, 4.9, label, LEFT, y, tracking=1.0))
        out.append("</g>")
        out.append(f'<g fill="{INK}">')
        out.append(text_path("Inter", 400, 7.4, value, LEFT + 40.0, y))
        out.append("</g>")

    # The code sits on its own quiet zone: 18 pt of bare ivory to the trim on the
    # right, 9 pt below, 34 pt to the nearest text, against the 4-module minimum.
    out += [
        f'<path fill="{INK}" d="{qr_d}"/>',
        "</svg>",
    ]
    return "\n".join(out)


# ------------------------------------------------------------------ render ---
def sh(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ! {' '.join(cmd[:2])}: {r.stderr.strip()[:200]}")


def main() -> int:
    for f in ("CrimsonPro.ttf", "CrimsonPro-Italic.ttf", "Inter.ttf"):
        if not (FONT_DIR / f).exists():
            print(f"missing font: {FONT_DIR / f}", file=sys.stderr)
            return 2

    art = monogram_art()
    faces = {"front": front(art), "back": back(art)}

    for name, svg in faces.items():
        svg_path = OUT / f"card-{name}.svg"
        svg_path.write_text(svg)
        print(f"wrote {svg_path.relative_to(HERE.parent.parent)}")

        pdf = OUT / f"card-{name}.pdf"
        sh(["rsvg-convert", "-f", "pdf", "-o", str(pdf), str(svg_path)])

        cmyk = OUT / f"card-{name}-cmyk.pdf"
        sh(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
            "-dProcessColorModel=/DeviceCMYK", "-sColorConversionStrategy=CMYK",
            f"-sOutputFile={cmyk}", str(pdf)])

        (OUT / "proof").mkdir(exist_ok=True)
        sh(["rsvg-convert", "-f", "png", "-d", "300", "-p", "300",
            "-b", "white", "-o", str(OUT / "proof" / f"card-{name}.png"), str(svg_path)])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
