#!/usr/bin/env python3
"""
Generate a KDP-ready wraparound paperback cover for "Unstuck" v2.
Assumes 6" x 9" trim size. Adjust PAGE_COUNT for correct spine width.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

# ==================== CONFIGURATION ====================
TRIM_W = 6.0       # inches
TRIM_H = 9.0       # inches
BLEED = 0.125      # inches
DPI = 300
PAGE_COUNT = 81    # <-- ADJUST THIS to your actual page count
PAPER_THICKNESS = 0.002252  # inches per page (KDP white paper)
# =======================================================

spine = PAGE_COUNT * PAPER_THICKNESS

total_w = TRIM_W * 2 + spine + BLEED * 2
total_h = TRIM_H + BLEED * 2

W = int(round(total_w * DPI))
H = int(round(total_h * DPI))

bleed_px = int(round(BLEED * DPI))
trim_w_px = int(round(TRIM_W * DPI))
trim_h_px = int(round(TRIM_H * DPI))
spine_px = int(round(spine * DPI))

# Coordinates
back_left = bleed_px
back_right = back_left + trim_w_px
spine_left = back_right
spine_right = spine_left + spine_px
front_left = spine_right
front_right = front_left + trim_w_px

safe_margin = int(round(0.25 * DPI))

# Colors
C_BG = (18, 18, 20)
C_BG_WARM = (22, 20, 18)
C_ACCENT = (255, 130, 0)       # vivid amber
C_ACCENT_GLOW = (255, 200, 120) # warm gold
C_TEXT = (245, 245, 245)
C_SUBTITLE = (0, 255, 255)  # electric cyan — very high contrast against dark bg
C_TEXT_DIM = (180, 180, 185)

# Fonts
FONT_ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ARIAL_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# ==================== CREATE BASE ====================
img = Image.new("RGB", (W, H), C_BG)
draw = ImageDraw.Draw(img)

# Add subtle warm radial glow from the crack center (front cover area)
# We do this by drawing many concentric ellipses with decreasing alpha
# Since we're in RGB mode, we simulate by blending colors.

random.seed(42)

# Background texture: fine noise
pixels = img.load()
for _ in range(80000):
    x = random.randint(0, W-1)
    y = random.randint(0, H-1)
    r, g, b = pixels[x, y]
    delta = random.randint(-10, 10)
    pixels[x, y] = (max(0, min(255, r+delta)), max(0, min(255, g+delta)), max(0, min(255, b+delta)))

# ==================== THE BREAK LINE ====================
# A sharp angular crack that widens from back to front.
# Defined by center line points and per-point widths.

crack_pts = [
    # (x, y, width)  -- y from top
    (back_left + int(1.0 * DPI),   int(8.85 * DPI),  6),
    (back_left + int(2.5 * DPI),   int(8.45 * DPI),  10),
    (spine_left + spine_px//3,     int(7.25 * DPI),  20),
    (spine_right,                    int(5.75 * DPI),  45),
    (front_left + int(1.0 * DPI),   int(4.85 * DPI),  140),
    (front_left + int(3.0 * DPI),   int(4.05 * DPI),  260),
    (front_left + int(5.2 * DPI),   int(3.25 * DPI),  180),
    (front_right + 100,  int(0 * DPI),  120),
]

def draw_smooth_polygon(draw, pts_left, pts_right, fill, outline=None):
    """Draw a smooth-ish polygon for the crack."""
    poly = list(pts_left) + list(reversed(pts_right))
    draw.polygon(poly, fill=fill)
    if outline:
        for i in range(len(poly)):
            p1 = poly[i]
            p2 = poly[(i+1) % len(poly)]
            draw.line([p1, p2], fill=outline, width=2)

# Build edges
left_edge = []
right_edge = []

for i in range(len(crack_pts)):
    x, y, w = crack_pts[i]
    if i < len(crack_pts) - 1:
        nx, ny, _ = crack_pts[i+1]
    else:
        nx, ny = x, y
    if i > 0:
        px, py, _ = crack_pts[i-1]
    else:
        px, py = x, y
    
    # Direction
    dx1 = x - px
    dy1 = y - py
    dx2 = nx - x
    dy2 = ny - y
    dx = (dx1 + dx2) / 2 if (dx1, dy1) != (0, 0) and (dx2, dy2) != (0, 0) else (dx2 if dx1 == 0 else dx1)
    dy = (dy1 + dy2) / 2 if (dx1, dy1) != (0, 0) and (dx2, dy2) != (0, 0) else (dy2 if dy1 == 0 else dy1)
    
    length = math.hypot(dx, dy) or 1
    perp_x = -dy / length
    perp_y = dx / length
    
    # Jagged variation
    jag = random.uniform(-0.12, 0.12) * w
    left_edge.append((x + perp_x * (w/2 + jag), y + perp_y * (w/2 + jag)))
    right_edge.append((x - perp_x * (w/2 + jag), y - perp_y * (w/2 + jag)))

# Draw main crack body
poly = left_edge + list(reversed(right_edge))
draw.polygon(poly, fill=C_ACCENT)

# Inner bright core (narrower version)
inner_scale = 0.35
ileft = [(x + (cx-x)*inner_scale, y + (cy-y)*inner_scale) for (x,y), (cx,cy) in zip(left_edge, [(sum([p[0] for p in left_edge])/len(left_edge), sum([p[1] for p in left_edge])/len(left_edge))]*len(left_edge))]
# Better: scale toward local centerline
ileft = []
iright = []
for i in range(len(crack_pts)):
    x, y, w = crack_pts[i]
    ileft.append((x + perp_x * (w*inner_scale/2), y + perp_y * (w*inner_scale/2)))
    iright.append((x - perp_x * (w*inner_scale/2), y - perp_y * (w*inner_scale/2)))
# Recompute with proper perp
ileft = []
iright = []
for i in range(len(crack_pts)):
    x, y, w = crack_pts[i]
    if i < len(crack_pts)-1:
        nx, ny, _ = crack_pts[i+1]
    else:
        nx, ny = x, y
    if i > 0:
        px, py, _ = crack_pts[i-1]
    else:
        px, py = x, y
    dx = (nx - px) / 2 if not (i == 0 or i == len(crack_pts)-1) else (nx-x if i==0 else x-px)
    dy = (ny - py) / 2 if not (i == 0 or i == len(crack_pts)-1) else (ny-y if i==0 else y-py)
    length = math.hypot(dx, dy) or 1
    perp_x = -dy / length
    perp_y = dx / length
    ileft.append((x + perp_x * w * inner_scale * 0.5, y + perp_y * w * inner_scale * 0.5))
    iright.append((x - perp_x * w * inner_scale * 0.5, y - perp_y * w * inner_scale * 0.5))

inner_poly = ileft + list(reversed(iright))
draw.polygon(inner_poly, fill=C_ACCENT_GLOW)

# Add glow halo around crack by drawing blurred larger polygon
# Since we can't blur easily without another image, we draw semi-transparent? No, RGB.
# Instead, draw outer feathered layers manually with smaller opacity steps.
# We'll simulate by drawing slightly larger polygons in progressively darker shades.
for scale, color in [(0.7, (200, 100, 20)), (0.85, (140, 70, 15)), (1.0, C_BG)]:
    # Skip the outermost since it's background
    if scale >= 1.0:
        continue
    oleft = []
    oright = []
    for i in range(len(crack_pts)):
        x, y, w = crack_pts[i]
        if i < len(crack_pts)-1:
            nx, ny, _ = crack_pts[i+1]
        else:
            nx, ny = x, y
        if i > 0:
            px, py, _ = crack_pts[i-1]
        else:
            px, py = x, y
        dx = (nx - px) / 2 if not (i == 0 or i == len(crack_pts)-1) else (nx-x if i==0 else x-px)
        dy = (ny - py) / 2 if not (i == 0 or i == len(crack_pts)-1) else (ny-y if i==0 else y-py)
        length = math.hypot(dx, dy) or 1
        perp_x = -dy / length
        perp_y = dx / length
        oleft.append((x + perp_x * w * scale * 0.5, y + perp_y * w * scale * 0.5))
        oright.append((x - perp_x * w * scale * 0.5, y - perp_y * w * scale * 0.5))
    opoly = oleft + list(reversed(oright))
    draw.polygon(opoly, fill=color)

# Redraw main crack on top
poly = left_edge + list(reversed(right_edge))
draw.polygon(poly, fill=C_ACCENT)
draw.polygon(inner_poly, fill=C_ACCENT_GLOW)

# ==================== FRONT COVER TEXT ====================

font_title = load_font(FONT_ARIAL_BLACK, 240)
font_subtitle = load_font(FONT_ARIAL_BOLD, 44)
font_author = load_font(FONT_ARIAL_BOLD, 42)
font_spine = load_font(FONT_ARIAL_BOLD, 48)
font_spine_small = load_font(FONT_ARIAL, 34)
font_back = load_font(FONT_ARIAL, 30)
font_back_small = load_font(FONT_ARIAL, 22)
font_quote = load_font(FONT_ARIAL_BOLD, 26)

# Title: UNSTUCK
# Place it so the crack runs behind/around it
title_text = "UNSTUCK"
tb = draw.textbbox((0, 0), title_text, font=font_title)
tw = tb[2] - tb[0]
th = tb[3] - tb[1]

title_x = front_left + (trim_w_px - tw) // 2
title_y = bleed_px + int(1.35 * DPI)

# Slight shadow for depth
for ox, oy in [(4, 4), (2, 2)]:
    draw.text((title_x + ox, title_y + oy), title_text, font=font_title, fill=(0, 0, 0))
draw.text((title_x, title_y), title_text, font=font_title, fill=C_TEXT)

# Subtitle
subtitle = "Brutal Guidance for Getting Out of\nYour Own Way"
lines = subtitle.split('\n')
line_h = int(0.18 * DPI)
for i, line in enumerate(lines):
    lb = draw.textbbox((0, 0), line, font=font_subtitle)
    lw = lb[2] - lb[0]
    lx = front_left + (trim_w_px - lw) // 2
    ly = title_y + th + int(0.45 * DPI) + i * line_h
    draw.text((lx, ly), line, font=font_subtitle, fill=C_SUBTITLE)

# Author
author = "PHILIP HUFFMAN"
ab = draw.textbbox((0, 0), author, font=font_author)
aw = ab[2] - ab[0]
ax = front_left + (trim_w_px - aw) // 2
ay = bleed_px + trim_h_px - int(0.75 * DPI) - ab[3]
draw.text((ax, ay), author, font=font_author, fill=C_TEXT_DIM)

# ==================== SPINE ====================

# Spine title (rotated)
spine_title = "UNSTUCK"
stb = draw.textbbox((0, 0), spine_title, font=font_spine)
stw = stb[2] - stb[0]
sth = stb[3] - stb[1]

st_img = Image.new("RGBA", (stw + 10, sth + 10), (0, 0, 0, 0))
st_draw = ImageDraw.Draw(st_img)
st_draw.text((5, 5), spine_title, font=font_spine, fill=C_TEXT)
st_img = st_img.rotate(270, expand=True)
img.paste(st_img, (spine_left + (spine_px - st_img.width)//2, bleed_px + int(0.9 * DPI)), st_img)

# Spine author
spine_auth = "PHILIP HUFFMAN"
sab = draw.textbbox((0, 0), spine_auth, font=font_spine_small)
saw = sab[2] - sab[0]
sah = sab[3] - sab[1]
sa_img = Image.new("RGBA", (saw + 10, sah + 10), (0, 0, 0, 0))
sa_draw = ImageDraw.Draw(sa_img)
sa_draw.text((5, 5), spine_auth, font=font_spine_small, fill=C_ACCENT_GLOW)
sa_img = sa_img.rotate(270, expand=True)
img.paste(sa_img, (spine_left + (spine_px - sa_img.width)//2, bleed_px + trim_h_px - sa_img.height - int(0.6 * DPI)), sa_img)

# ==================== BACK COVER ====================

# Blurb
blurb = (
    "Most obstacles are not external.\n"
    "They are internal negotiations\n"
    "we have learned to accept.\n\n"
    "UNSTUCK rejects motivational fluff\n"
    "and insists on discipline, responsibility,\n"
    "and daily action.\n\n"
    "Drawing on Stoic wisdom, it argues that\n"
    "the right response to uncertainty is not\n"
    "prediction—but character.\n\n"
    "Stop waiting. Move now."
)

blurb_lines = blurb.split('\n')
blurb_x = back_left + safe_margin
blurb_y = bleed_px + int(1.1 * DPI)
for i, line in enumerate(blurb_lines):
    ly = blurb_y + i * int(0.2 * DPI)
    draw.text((blurb_x, ly), line, font=font_back, fill=C_TEXT)

# Stoic quote at bottom of back cover
quote = '"The happiness of your life depends upon\nthe quality of your thoughts."\n— Marcus Aurelius'
quote_lines = quote.split('\n')
qy = bleed_px + trim_h_px - safe_margin - int(1.8 * DPI)
for i, line in enumerate(quote_lines):
    ly = qy + i * int(0.16 * DPI)
    draw.text((blurb_x, ly), line, font=font_quote, fill=C_ACCENT_GLOW)

# 8 Principles (very small, above quote)
principles = (
    "1. Stop Stalling   2. Your Excuses Are BS   3. Embrace Discomfort   4. Don\u2019t Negotiate\n"
    "5. Action Comes First   6. Stack Wins   7. Persistence Over Perfection   8. Don\u2019t Miss Twice"
)
# Word wrap
words = principles.replace('\n', ' ').split()
max_w = trim_w_px - safe_margin * 2
line = ""
line_idx = 0
pr_y = qy - int(0.5 * DPI)
for word in words:
    test = line + word + "  "
    tb = draw.textbbox((0, 0), test, font=font_back_small)
    if (tb[2] - tb[0]) > max_w and line:
        draw.text((blurb_x, pr_y + line_idx * int(0.14 * DPI)), line.strip(), font=font_back_small, fill=C_TEXT_DIM)
        line = word + "  "
        line_idx += 1
    else:
        line = test
draw.text((blurb_x, pr_y + line_idx * int(0.14 * DPI)), line.strip(), font=font_back_small, fill=C_TEXT_DIM)

# Barcode area (white box)
barcode_w = int(2.0 * DPI)
barcode_h = int(1.2 * DPI)
barcode_x = back_right - safe_margin - barcode_w
barcode_y = bleed_px + trim_h_px - safe_margin - barcode_h
draw.rectangle(
    [(barcode_x, barcode_y), (barcode_x + barcode_w, barcode_y + barcode_h)],
    fill=(245, 245, 245),
    outline=(180, 180, 180),
    width=2
)

# ==================== SAFE AREA GUIDES (optional, for preview) ====================
# Uncomment below to draw faint red lines showing safe area boundaries.
# These should NOT be in the final KDP upload.
#
# SAFE_COLOR = (255, 0, 0)
# # Front safe area
# draw.rectangle([front_left + safe_margin, bleed_px + safe_margin, front_right - safe_margin, bleed_px + trim_h_px - safe_margin], outline=SAFE_COLOR, width=2)
# # Back safe area
# draw.rectangle([back_left + safe_margin, bleed_px + safe_margin, back_right - safe_margin, bleed_px + trim_h_px - safe_margin], outline=SAFE_COLOR, width=2)

# ==================== SAVE ====================
img.save("unstuck_cover_v2.png", "PNG")

# PDF export
pdf_path = "unstuck_cover_kdp.pdf"
pdf_w = total_w * 72
pdf_h = total_h * 72

buf = io.BytesIO()
img.save(buf, format="PNG", dpi=(DPI, DPI))
buf.seek(0)

c = canvas.Canvas(pdf_path, pagesize=(pdf_w, pdf_h))
c.drawImage(ImageReader(buf), 0, 0, width=pdf_w, height=pdf_h)
c.save()

print(f"✓ Cover generated: {W}x{H} pixels @ {DPI} DPI")
print(f"✓ Dimensions: {total_w:.3f}\" x {total_h:.3f}\" (including bleed)")
print(f"✓ Spine width: {spine:.3f}\" ({PAGE_COUNT} pages, white paper)")
print(f"✓ Files saved: unstuck_cover_v2.png, {pdf_path}")
print(f"\nNOTE: Adjust PAGE_COUNT in this script to match your actual manuscript.")
print(f"Current assumption: {PAGE_COUNT} pages.")
print(f"If using cream paper, change PAPER_THICKNESS to 0.0025.")
