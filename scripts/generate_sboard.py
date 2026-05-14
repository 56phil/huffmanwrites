#!/usr/bin/env python3
"""Generate Stoic Backgammon chapter hero images.
Each chapter gets a distinct board position.
Outputs both landscape (16x9) and portrait (4x5) PNGs.
Usage: python3 generate_sboard.py
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

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

# Palette
COLOR_BG = (5, 5, 30)              # Nearly-black Midnight Blue
COLOR_BORDER = (192, 192, 192)     # Polished Silver
COLOR_BAR = (192, 192, 192)       # Polished Silver
COLOR_TEXT = (255, 255, 255)       # White
COLOR_GOLD = (184, 134, 11)        # Dark Goldenrod
COLOR_SILVER = (224, 224, 224)     # Bright Silver
COLOR_C_BLACK = (0, 0, 0)           # Deep Black
COLOR_C_WHITE = (250, 235, 215)    # Antique White
COLOR_CUBE = (220, 220, 220)       # Light Gray/Silver for cube

def generate(canvas_size, checkers, cube_val=64, title=""):
    """
    checkers: list of (point_index, n_checkers, color)
    point_index: 1-24 (standard), 0 for the bar
    color: 'w' or 'b'
    """
    W, H = canvas_size
    scale = min(W / OUTER_W, H / OUTER_H)
    
    px_frame = FRAME * scale
    px_bar_w = BAR_WIDTH * scale
    px_point_base = POINT_BASE * scale
    px_point_h = POINT_HEIGHT * scale
    px_gap = OPPOSITE_GAP * scale
    checker_r = 0.45 * scale
    
    offset_x = (W - INNER_W * scale - 2 * px_frame) / 2
    offset_y = (H - INNER_H * scale - 2 * px_frame) / 2
    board_left = offset_x + px_frame
    board_top = offset_y + px_frame
    board_right = board_left + INNER_W * scale
    board_bottom = board_top + INNER_H * scale
    bar_left = board_left + SUB_BOARD_W * scale
    bar_right = bar_left + px_bar_w
    
    img = Image.new('RGB', (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img)
    
    # Border
    draw.rectangle([offset_x, offset_y, offset_x + INNER_W * scale + 2 * px_frame,
                    offset_y + INNER_H * scale + 2 * px_frame], fill=COLOR_BORDER)
    
    # Board Surface
    draw.rectangle([board_left, board_top, board_right, board_bottom], fill=COLOR_BG)
    # Bar
    draw.rectangle([bar_left, board_top, bar_right, board_bottom], fill=COLOR_BAR)
    
    def draw_top_points(left, start_idx, colors, n=6):
        for i in range(n):
            x1, x2 = left + i * px_point_base, left + (i + 1) * px_point_base
            xm = (x1 + x2) / 2
            pt_color = colors[(start_idx - i) % 2]
            draw.polygon([(x1, board_top), (x2, board_top), (xm, board_top + px_point_h)],
                        fill=pt_color)

    def draw_bottom_points(left, start_idx, colors, n=6):
        for i in range(n):
            x1, x2 = left + i * px_point_base, left + (i + 1) * px_point_base
            xm = (x1 + x2) / 2
            pt_color = colors[(start_idx + i) % 2]
            draw.polygon([(x1, board_bottom), (x2, board_bottom), (xm, board_bottom - px_point_h)],
                        fill=pt_color)
    
    pt_colors = {0: COLOR_GOLD, 1: COLOR_SILVER}
    
    draw_top_points(board_left, 24, pt_colors)
    draw_top_points(bar_right, 18, pt_colors)
    draw_bottom_points(board_left, 1, pt_colors)
    draw_bottom_points(bar_right, 13, pt_colors)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", int(checker_r * 1.2))
    except:
        font = ImageFont.load_default()

    # Doubling Cube
    cube_size = 0.6 * scale
    cube_cx = (bar_left + bar_right) / 2
    cube_cy = (board_top + board_bottom) / 2
    draw.rectangle([cube_cx - cube_size/2, cube_cy - cube_size/2, cube_cx + cube_size/2, cube_cy + cube_size/2], 
                    fill=COLOR_CUBE, outline=COLOR_C_BLACK, width=1)
    
    cube_text = str(cube_val)
    bbox = draw.textbbox((0, 0), cube_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cube_cx - tw/2, cube_cy - th/2), cube_text, fill=COLOR_C_BLACK, font=font)

    # Draw checkers
    for point, n, color in checkers:
        if point == 0: # THE BAR
            cx = (bar_left + bar_right) / 2
            if color == 'w':
                cy = board_bottom - (2.5 * scale + checker_r)
            else:
                cy = board_top + (2.5 * scale + checker_r)
            fill = COLOR_C_WHITE if color == 'w' else COLOR_C_BLACK
            draw.ellipse([cx - checker_r, cy - checker_r, cx + checker_r, cy + checker_r], 
                        fill=fill, outline=COLOR_C_BLACK, width=1)
            text_str = str(n)
            bbox = draw.textbbox((0, 0), text_str, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            text_color = COLOR_C_BLACK if color == 'w' else COLOR_C_WHITE
            draw.text((cx - tw/2, cy - th/2), text_str, fill=text_color, font=font)
            continue

        if 1 <= point <= 6: # Bottom Left
            cx = board_left + (point - 1 + 0.5) * px_point_base
            edge_y = board_bottom
            direction = -1
        elif 7 <= point <= 12: # Bottom Right
            # Mirroring the Bottom Left logic for a "Chess-like" mirroring
            # If BL 1 is far left, BR 12 is far right.
            # The x relative to bar_right should be (point - 7 + 0.5) * px_point_base
            # Let's check: point 12 (closest to bar) -> 12-7=5. 5.5*base.
            # point 7 (farthest right) -> 7-7=0. 0.5*base.
            # Wait, if we want mirror: 
            # BL Point 1 (far left) <-> BR Point 12 (far right)
            # BL Point 6 (near bar) <-> BR Point 7 (near bar)
            # So BR X = bar_right + (point - 7 + 0.5) * px_point_base
            # Let's test: Point 7 (near bar) -> 7-7+0.5 = 0.5. (Correct)
            # Point 12 (far right) -> 12-7+0.5 = 5.5. (Correct)
            cx = bar_right + (point - 7 + 0.5) * px_point_base
            edge_y = board_bottom
            direction = -1
        elif 13 <= point <= 18: # Top Right
            # Point 18 is near bar, Point 13 is far right.
            cx = bar_right + (18 - point + 0.5) * px_point_base
            edge_y = board_top
            direction = 1
        elif 19 <= point <= 24: # Top Left
            # Point 19 is near bar, Point 24 is far left.
            cx = board_left + (24 - point + 0.5) * px_point_base
            edge_y = board_top
            direction = 1
        else:
            continue 
            
        for j in range(n):
            cy = edge_y + direction * (2 * checker_r * j + checker_r)
            fill = COLOR_C_WHITE if color == 'w' else COLOR_C_BLACK
            draw.ellipse([cx - checker_r, cy - checker_r, cx + checker_r, cy + checker_r], 
                        fill=fill, outline=COLOR_C_BLACK, width=1)
    
    return img

# --- Corrected Starting Position ---
STARTING_POS = [
    (1, 2, 'w'), 
    (6, 5, 'b'), 
    (8, 3, 'b'), 
    (12, 5, 'w'), 
    (13, 5, 'b'), 
    (17, 3, 'w'), 
    (19, 5, 'w'), 
    (24, 2, 'b'),
]

OUT = "/Users/prh/Developer/huffmanwrites/static/img/articles"
os.makedirs(OUT, exist_ok=True)

for slug, pos in [("sb-starting-position", STARTING_POS)]:
    l = generate(LANDSCAPE, pos, cube_val=64)
    p = generate(PORTRAIT, pos, cube_val=64)
    l.save(f"{OUT}/{slug} 16x9.png")
    p.save(f"{OUT}/{slug} 4x5.png")
    print(f"Saved {slug} 16x9.png + 4x5.png")

print("Done.")
