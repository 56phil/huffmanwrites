#!/usr/bin/env python3
"""
Generate a KDP-ready wraparound paperback cover for "Unstuck".
Assumes 6" x 9" trim size. Adjust PAGE_COUNT for correct spine width.
"""

import math
import random
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

# ==================== CONFIGURATION ====================
TRIM_W = 6.0       # inches
TRIM_H = 9.0       # inches
BLEED = 0.125      # inches
DPI = 300
PAGE_COUNT = 180   # <-- ADJUST THIS to your actual page count
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

# Safe margins (0.25" from trim)
safe_margin = int(round(0.25 * DPI))

# Colors
C_BG_DARK = (15, 15, 15)
C_BG_MID = (28, 28, 28)
C_BG_LIGHT = (245, 245, 245)
C_ACCENT = (232, 93, 4)       # deep orange
C_ACCENT_LIGHT = (244, 162, 97)  # warm gold
C_TEXT_LIGHT = (250, 250, 250)
C_TEXT_DARK = (10, 10, 10)

# Fonts
FONT_ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ARIAL_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Create base image
img = Image.new("RGB", (W, H), C_BG_DARK)
draw = ImageDraw.Draw(img)

# ========================================================
# BACKGROUND: Continuous gradient + texture
# ========================================================

# Create a subtle horizontal noise/texture background
random.seed(42)
for y in range(H):
    # Overall gradient: dark on left (back), slightly lighter on right (front)
    t = y / H
    # Actually we want a vertical gradient too: darker at bottom, lighter at top
    # But the main story is left-to-right (back to front)
    base_r = 15 + int((y / H) * 8)
    base_g = 15 + int((y / H) * 8)
    base_b = 15 + int((y / H) * 8)
    
    for x in range(W):
        # Left-to-right: back is darker, front is lighter where the "opening" is
        progress = x / W
        # Add subtle grain
        noise = random.randint(-6, 6)
        val = max(0, min(255, base_r + int(progress * 12) + noise))
        # We draw line by line for the base
        # But this is slow in pure Python. Let's do a faster approximation.
        pass

# Faster approach: draw rectangles for bands
for y in range(0, H, 4):
    brightness = 15 + int((y / H) * 10)
    draw.rectangle([(0, y), (W, min(y+4, H))], fill=(brightness, brightness, brightness))

# Add noise texture using random points (fast enough)
for _ in range(15000):
    x = random.randint(0, W-1)
    y = random.randint(0, H-1)
    base = img.getpixel((x, y))
    offset = random.randint(-12, 12)
    c = max(0, min(255, base[0] + offset))
    draw.point((x, y), fill=(c, c, c))

# ========================================================
# THE CRACK / OPENING (continuous from back to front)
# ========================================================
# The crack starts thin on the back cover bottom-left,
# runs through the spine, and opens wide on the front cover top-right.
# It represents breaking through being stuck.

def draw_crack(draw, W, H, back_left, back_right, spine_left, spine_right, front_left, front_right, bleed_px, trim_h_px):
    # Define the crack path as a series of polygons
    # Back cover: thin line, lower portion
    # Front cover: wide angular opening, upper-middle
    
    # Key points along the path (x, y, width)
    # y is from top (0) to bottom (H)
    # On back cover, crack is near bottom, thin
    p1 = (back_left + int(1.2 * DPI), int(7.8 * DPI))   # back, 1.2" from left, 7.8" from top
    w1 = 8
    
    # Spine entry
    p2 = (spine_left + spine_px // 2, int(6.5 * DPI))
    w2 = 18
    
    # Spine exit
    p3 = (spine_right - 10, int(5.0 * DPI))
    w3 = 35
    
    # Front cover: opens wide
    p4 = (front_left + int(1.5 * DPI), int(3.5 * DPI))
    w4 = 180
    
    p5 = (front_left + int(4.5 * DPI), int(2.5 * DPI))
    w5 = 280
    
    # Front cover top-right flare
    p6 = (front_right - int(0.8 * DPI), int(1.2 * DPI))
    w6 = 120
    
    points = [p1, p2, p3, p4, p5, p6]
    widths = [w1, w2, w3, w4, w5, w6]
    
    # Draw the crack as a series of filled polygons
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        w_start = widths[i]
        w_end = widths[i+1]
        
        # Calculate perpendicular direction
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        perp_x = -dy / length
        perp_y = dx / length
        
        # Build polygon
        steps = max(3, int(length / 8))
        left_edge = []
        right_edge = []
        
        for s in range(steps + 1):
            t = s / steps
            x = x1 + dx * t
            y = y1 + dy * t
            w = w_start + (w_end - w_start) * t
            # Add jaggedness
            jag = random.uniform(-w*0.15, w*0.15)
            left_edge.append((x + perp_x * (w/2 + jag), y + perp_y * (w/2 + jag)))
            right_edge.append((x - perp_x * (w/2 + jag), y - perp_y * (w/2 + jag)))
        
        polygon = left_edge + right_edge[::-1]
        
        # Color gradient along crack: darker orange inside, brighter at edges
        draw.polygon(polygon, fill=C_ACCENT)
        
        # Inner glow
        inner_poly = []
        for px, py in polygon:
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            inner_poly.append((cx + (px - cx) * 0.6, cy + (py - cy) * 0.6))
        try:
            draw.polygon(inner_poly, fill=(255, 140, 60))
        except Exception:
            pass

random.seed(42)
draw_crack(draw, W, H, back_left, back_right, spine_left, spine_right, front_left, front_right, bleed_px, trim_h_px)

# ========================================================
# FRONT COVER TEXT
# ========================================================

# Title: UNSTUCK
font_title = load_font(FONT_ARIAL_BLACK, 220)
font_subtitle = load_font(FONT_ARIAL_BOLD, 42)
font_author = load_font(FONT_ARIAL_BOLD, 36)
font_spine = load_font(FONT_ARIAL_BOLD, 44)
font_spine_small = load_font(FONT_ARIAL, 32)
font_back = load_font(FONT_ARIAL, 28)
font_back_small = load_font(FONT_ARIAL, 22)

# Front title position: centered horizontally on front cover, upper-middle
# But place it across the "opening"
title_text = "UNSTUCK"
# Measure
bbox = draw.textbbox((0, 0), title_text, font=font_title)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]

title_x = front_left + (trim_w_px - tw) // 2
title_y = bleed_px + int(1.4 * DPI)  # 1.4" from top trim

# Shadow for depth
shadow_offset = 6
draw.text((title_x + shadow_offset, title_y + shadow_offset), title_text, font=font_title, fill=(0, 0, 0))
draw.text((title_x, title_y), title_text, font=font_title, fill=C_TEXT_LIGHT)

# Subtitle
subtitle_text = "Brutal Guidance for Getting\nOut of Your Own Way"
bbox = draw.textbbox((0, 0), subtitle_text, font=font_subtitle)
sw = bbox[2] - bbox[0]
sh = bbox[3] - bbox[1]
sub_x = front_left + (trim_w_px - sw) // 2
sub_y = title_y + th + int(0.25 * DPI)

# Draw subtitle line by line
lines = subtitle_text.split('\n')
line_h = sh // len(lines)
for i, line in enumerate(lines):
    lb = draw.textbbox((0, 0), line, font=font_subtitle)
    lw = lb[2] - lb[0]
    lx = front_left + (trim_w_px - lw) // 2
    ly = sub_y + i * int(line_h * 1.2)
    draw.text((lx, ly), line, font=font_subtitle, fill=C_TEXT_LIGHT)

# Author
author_text = "PHILIP HUFFMAN"
bbox = draw.textbbox((0, 0), author_text, font=font_author)
aw = bbox[2] - bbox[0]
auth_x = front_left + (trim_w_px - aw) // 2
auth_y = front_left + int(4.8 * DPI)  # Actually from top
auth_y = bleed_px + int(4.8 * DPI)
draw.text((auth_x, auth_y), author_text, font=font_author, fill=C_ACCENT_LIGHT)

# ========================================================
# SPINE TEXT
# ========================================================

# Create a temporary rotated image for spine text
spine_text = "UNSTUCK"
st_bbox = draw.textbbox((0, 0), spine_text, font=font_spine)
st_w = st_bbox[2] - st_bbox[0]
st_h = st_bbox[3] - st_bbox[1]

# Spine text image
spine_img = Image.new("RGBA", (st_w + 20, st_h + 20), (0, 0, 0, 0))
spine_draw = ImageDraw.Draw(spine_img)
spine_draw.text((10, 10), spine_text, font=font_spine, fill=C_TEXT_LIGHT)
spine_img = spine_img.rotate(90, expand=True)

# Paste on spine, centered
spine_img_w, spine_img_h = spine_img.size
spine_text_x = spine_left + (spine_px - spine_img_w) // 2
spine_text_y = bleed_px + int(1.0 * DPI)
img.paste(spine_img, (spine_text_x, spine_text_y), spine_img)

# Author on spine (bottom)
spine_auth = "PHILIP HUFFMAN"
sa_bbox = draw.textbbox((0, 0), spine_auth, font=font_spine_small)
sa_w = sa_bbox[2] - sa_bbox[0]
sa_h = sa_bbox[3] - sa_bbox[1]
sa_img = Image.new("RGBA", (sa_w + 10, sa_h + 10), (0, 0, 0, 0))
sa_draw = ImageDraw.Draw(sa_img)
sa_draw.text((5, 5), spine_auth, font=font_spine_small, fill=C_ACCENT_LIGHT)
sa_img = sa_img.rotate(90, expand=True)
sa_img_w, sa_img_h = sa_img.size
sa_x = spine_left + (spine_px - sa_img_w) // 2
sa_y = bleed_px + trim_h_px - sa_img_h - int(0.5 * DPI)
img.paste(sa_img, (sa_x, sa_y), sa_img)

# ========================================================
# BACK COVER
# ========================================================

# Blurb
blurb = (
    "Most obstacles are not external.\n"
    "They are internal negotiations\n"
    "we have learned to accept.\n\n"
    "UNSTUCK rejects motivational fluff\n"
    "and insists on discipline, responsibility,\n"
    "and daily action.\n\n"
    "Stop waiting. Move now."
)

blurb_y = bleed_px + int(1.2 * DPI)
blurb_x = back_left + safe_margin

lines = blurb.split('\n')
for i, line in enumerate(lines):
    ly = blurb_y + i * int(0.22 * DPI)
    draw.text((blurb_x, ly), line, font=font_back, fill=C_TEXT_LIGHT)

# 8 Principles (small text, lower back)
principles = (
    "1. Stop Stalling  ·  2. Your Excuses Are BS  ·  3. Embrace Discomfort  ·  4. Don't Negotiate\n"
    "5. Action Comes First  ·  6. Stack Wins  ·  7. Persistence Over Perfection  ·  8. Don't Miss Twice"
)

# Draw principles above barcode area
pr_y = bleed_px + trim_h_px - safe_margin - int(1.6 * DPI)
pr_x = back_left + safe_margin
# Word wrap roughly
words = principles.replace('\n', ' ').split()
max_back_text_w = trim_w_px - safe_margin * 2
line = ""
line_idx = 0
for word in words:
    test = line + word + " "
    tb = draw.textbbox((0, 0), test, font=font_back_small)
    if (tb[2] - tb[0]) > max_back_text_w and line:
        draw.text((pr_x, pr_y + line_idx * int(0.16 * DPI)), line.strip(), font=font_back_small, fill=(180, 180, 180))
        line = word + " "
        line_idx += 1
    else:
        line = test
draw.text((pr_x, pr_y + line_idx * int(0.16 * DPI)), line.strip(), font=font_back_small, fill=(180, 180, 180))

# Barcode area (white rectangle, bottom right of back cover)
# KDP barcode: 2" x 1.2", 0.25" from bottom and right of trim
barcode_w = int(2.0 * DPI)
barcode_h = int(1.2 * DPI)
barcode_x = back_right - safe_margin - barcode_w  # 0.25" from right trim
barcode_y = bleed_px + trim_h_px - safe_margin - barcode_h  # 0.25" from bottom trim

# Draw a subtle outline, fill with slightly lighter dark (not pure white, but distinct)
# Actually KDP says barcode will be placed there; white or very light is best.
draw.rectangle(
    [(barcode_x, barcode_y), (barcode_x + barcode_w, barcode_y + barcode_h)],
    fill=(240, 240, 240),
    outline=(200, 200, 200),
    width=2
)

# ========================================================
# GUIDE LINES (for reference, not drawn)
# We don't draw crop marks on the actual PDF for KDP
# ========================================================

# Save high-res PNG
img.save("unstuck_cover_wraparound.png", "PNG")

# Convert to PDF using reportlab, preserving dimensions
pdf_path = "unstuck_cover_kdp.pdf"
pdf_w = total_w * 72  # points (1 inch = 72 pt)
pdf_h = total_h * 72

buf = io.BytesIO()
img.save(buf, format="PNG", dpi=(DPI, DPI))
buf.seek(0)

c = canvas.Canvas(pdf_path, pagesize=(pdf_w, pdf_h))
c.drawImage(ImageReader(buf), 0, 0, width=pdf_w, height=pdf_h)
c.save()

print(f"Cover generated: {W}x{H} pixels @ {DPI} DPI")
print(f"Dimensions: {total_w}\" x {total_h}\" (including bleed)")
print(f"Spine width: {spine:.3f}\" ({PAGE_COUNT} pages, white paper)")
print(f"Files saved: unstuck_cover_wraparound.png, {pdf_path}")
print(f"\nIMPORTANT: Adjust PAGE_COUNT in this script to match your book.")
print(f"Current assumption: {PAGE_COUNT} pages.")
