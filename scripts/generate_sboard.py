#!/usr/bin/env python3
"""Generate Stoic Backgammon chapter hero images.
Each chapter gets a distinct board position.
Outputs both landscape (16x9) and portrait (4x5) PNGs.
Usage: python3 generate_sb_heroes.py
"""
import os, math
from PIL import Image, ImageDraw

# Canvas sizes
LANDSCAPE = (1024, 576)
PORTRAIT = (1024, 1280)

# Geometry (checker diameter = 1 unit)
UNIT = 80
POINT_BASE = 1.0
POINT_HEIGHT = 5.05
OPPOSITE_GAP = 0.75
BAR_WIDTH = 1.0625
FRAME = 0.5

SUB_BOARD_W = 6.0
INNER_W = 2 * SUB_BOARD_W + BAR_WIDTH  # 13.0625
INNER_H = 2 * POINT_HEIGHT + OPPOSITE_GAP  # 10.85
OUTER_W = INNER_W + 2 * FRAME
OUTER_H = INNER_H + 2 * FRAME

# Colors
bg = (20, 20, 20)
frame = (100, 70, 40)
board = (140, 95, 55)
bar = (110, 80, 45)
pt_light = (210, 180, 140)
pt_dark = (40, 40, 40)
white_checker = (240, 240, 230)
black_checker = (30, 30, 30)

def generate(canvas_size, checkers, title=""):
    """checkers: list of (x_quadrant, point_index, n_checkers, color) where
    x_quadrant is 0,1,2,3 for UL, UR, LL, LR and point_index 0-5 from bar outward
    """
    W, H = canvas_size
    scale = min(W / OUTER_W, H / OUTER_H)
    
    px_frame = FRAME * scale
    px_bar_w = BAR_WIDTH * scale
    px_point_base = POINT_BASE * scale
    px_point_h = POINT_HEIGHT * scale
    px_gap = OPPOSITE_GAP * scale
    checker_r = 0.45 * scale  # slightly less than 0.5 to avoid touching
    offset_x = (W - INNER_W * scale - 2 * px_frame) / 2
    offset_y = (H - INNER_H * scale - 2 * px_frame) / 2
    board_left = offset_x + px_frame
    board_top = offset_y + px_frame
    board_right = board_left + INNER_W * scale
    board_bottom = board_top + INNER_H * scale
    bar_left = board_left + SUB_BOARD_W * scale
    bar_right = bar_left + px_bar_w
    
    img = Image.new('RGB', (W, H), bg)
    draw = ImageDraw.Draw(img)
    
    # Frame, board, bar
    draw.rectangle([offset_x, offset_y, offset_x + INNER_W * scale + 2 * px_frame,
                    offset_y + INNER_H * scale + 2 * px_frame], fill=frame)
    draw.rectangle([board_left, board_top, board_right, board_bottom], fill=board)
    draw.rectangle([bar_left, board_top, bar_right, board_bottom], fill=bar)
    
    def draw_top_points(left, colors, n=6):
        for i in range(n):
            x1, x2 = left + i * px_point_base, left + (i + 1) * px_point_base
            xm = (x1 + x2) / 2
            draw.polygon([(x1, board_top), (x2, board_top), (xm, board_top + px_point_h)],
                        fill=colors[i % 2])
    def draw_bottom_points(left, colors, n=6):
        for i in range(n):
            x1, x2 = left + i * px_point_base, left + (i + 1) * px_point_base
            xm = (x1 + x2) / 2
            draw.polygon([(x1, board_bottom), (x2, board_bottom), (xm, board_bottom - px_point_h)],
                        fill=colors[i % 2])
    
    lt, lb = [pt_dark, pt_light], [pt_light, pt_dark]
    rt, rb = [pt_light, pt_dark], [pt_dark, pt_light]
    draw_top_points(board_left, lt); draw_top_points(bar_right, rt)
    draw_bottom_points(board_left, lb); draw_bottom_points(bar_right, rb)
    
    # Draw checkers
    for q, pi, n, color in checkers:
        cx = (board_left if q in (0, 2) else bar_right) + (pi + 0.5) * px_point_base
        apex_y = board_top + px_point_h if q in (0, 1) else board_bottom - px_point_h
        direction = 1 if q in (2, 3) else -1
        for j in range(n):
            cy = apex_y + direction * (2 * checker_r * j + checker_r * 1.5)
            fill = white_checker if color == 'w' else black_checker
            draw.ellipse([cx - checker_r, cy - checker_r, cx + checker_r, cy + checker_r], fill=fill)
    
    return img

# --- Define chapter positions ---

# Standard opening
OPENING = [
    (0, 5, 2, 'w'), (1, 5, 2, 'b'),  # 24-point / 1-point
    (0, 4, 5, 'w'), (1, 4, 5, 'b'),  # 13-point / 12-point
    (0, 3, 3, 'w'), (1, 3, 3, 'b'),  # 8-point / 17-point
    (0, 2, 5, 'w'), (1, 2, 5, 'b'),  # 6-point / 19-point
]

# Mid-blitz position
BLITZ = [
    (0, 5, 2, 'w'), (1, 5, 1, 'b'),
    (0, 4, 4, 'w'), (0, 3, 3, 'w'),
    (2, 5, 2, 'b'), (2, 4, 5, 'b'),
    (3, 5, 1, 'w'), (3, 2, 3, 'b'), (3, 1, 2, 'b'),
]

# Bearing off end-game
BEAR_OFF = [
    (0, 0, 3, 'w'), (0, 1, 2, 'w'),
    (2, 5, 2, 'b'), (2, 4, 3, 'b'),
]

# Save
OUT = "/Users/prh/Developer/huffmanwrites/static/img/articles"
os.makedirs(OUT, exist_ok=True)

for slug, pos in [("sb-sample-opening", OPENING), ("sb-sample-blitz", BLITZ), ("sb-sample-bearoff", BEAR_OFF)]:
    l = generate(LANDSCAPE, pos)
    p = generate(PORTRAIT, pos)
    l.save(f"{OUT}/{slug} 16x9.png")
    p.save(f"{OUT}/{slug} 4x5.png")
    print(f"Saved {slug} 16x9.png + 4x5.png")

print("Done.")
