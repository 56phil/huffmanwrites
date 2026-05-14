#!/usr/bin/env python3
"""Generate the 'sb-order-disorder' Stoic Backgammon board position."""
import os
from PIL import Image, ImageDraw, ImageFont

# Supersampling factor
SS = 4

# Canvas sizes
LANDSCAPE = (1024, 576)
PORTRAIT = (1024, 1280)

# Geometry
POINT_BASE = 1.0
POINT_HEIGHT = 5.05
OPPOSITE_GAP = 0.75
BAR_WIDTH = 1.0625
FRAME = 0.5

SUB_BOARD_W = 6.0
INNER_W = 2 * SUB_BOARD_W + BAR_WIDTH
INNER_H = 2 * POINT_HEIGHT + OPPOSITE_GAP
OUTER_W = INNER_W + 2 * FRAME
OUTER_H = INNER_H + 2 * FRAME

COLOR_BG = (5, 5, 30)
COLOR_BORDER = (192, 192, 192)
COLOR_BAR = (192, 192, 192)
COLOR_GOLD = (184, 134, 11)
COLOR_SILVER = (224, 224, 224)
COLOR_C_BLACK = (0, 0, 0)
COLOR_C_WHITE = (250, 235, 215)
COLOR_CUBE = (220, 220, 220)

def generate(canvas_size, checkers, cube_val=64):
    W, H = canvas_size
    sW, sH = W * SS, H * SS
    scale = min(sW / OUTER_W, sH / OUTER_H)
    
    px_frame = FRAME * scale
    px_bar_w = BAR_WIDTH * scale
    px_point_base = POINT_BASE * scale
    px_point_h = POINT_HEIGHT * scale
    checker_r = 0.45 * scale
    
    offset_x = (sW - INNER_W * scale - 2 * px_frame) / 2
    offset_y = (sH - INNER_H * scale - 2 * px_frame) / 2
    board_left = offset_x + px_frame
    board_top = offset_y + px_frame
    board_right = board_left + INNER_W * scale
    board_bottom = board_top + INNER_H * scale
    bar_left = board_left + SUB_BOARD_W * scale
    bar_right = bar_left + px_bar_w
    
    img = Image.new('RGB', (sW, sH), COLOR_BG)
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([offset_x, offset_y, offset_x + INNER_W * scale + 2 * px_frame,
                    offset_y + INNER_H * scale + 2 * px_frame], fill=COLOR_BORDER)
    draw.rectangle([board_left, board_top, board_right, board_bottom], fill=COLOR_BG)
    draw.rectangle([bar_left, board_top, bar_right, board_bottom], fill=COLOR_BAR)
    
    def draw_top_points(left, start_idx, colors, n=6):
        for i in range(n):
            x1, x2 = left + i * px_point_base, left + (i + 1) * px_point_base
            xm = (x1 + x2) / 2
            pt_color = colors[(start_idx - i) % 2]
            draw.polygon([(x1, board_top), (x2, board_top), (xm, board_top + px_point_h)], fill=pt_color)

    def draw_bottom_points(left, start_idx, colors, n=6):
        for i in range(n):
            x1, x2 = left + i * px_point_base, left + (i + 1) * px_point_base
            xm = (x1 + x2) / 2
            pt_color = colors[(start_idx + i) % 2]
            draw.polygon([(x1, board_bottom), (x2, board_bottom), (xm, board_bottom - px_point_h)], fill=pt_color)
    
    pt_colors = {0: COLOR_GOLD, 1: COLOR_SILVER}
    draw_top_points(board_left, 24, pt_colors)
    draw_top_points(bar_right, 18, pt_colors)
    draw_bottom_points(board_left, 1, pt_colors)
    draw_bottom_points(bar_right, 13, pt_colors)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", int(checker_r * 1.2))
    except:
        font = ImageFont.load_default()

    cube_size = 0.6 * scale
    cube_cx = (bar_left + bar_right) / 2
    cube_cy = (board_top + board_bottom) / 2
    draw.rectangle([cube_cx - cube_size/2, cube_cy - cube_size/2, cube_cx + cube_size/2, cube_cy + cube_size/2], 
                    fill=COLOR_CUBE, outline=COLOR_C_BLACK, width=1)
    
    cube_text = str(cube_val)
    bbox = draw.textbbox((0, 0), cube_text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cube_cx - tw/2, cube_cy - th/2), cube_text, fill=COLOR_C_BLACK, font=font)

    for point, n, color in checkers:
        if point == 0:
            cx = (bar_left + bar_right) / 2
            cy = board_bottom - (2.5 * scale + checker_r) if color == 'w' else board_top + (2.5 * scale + checker_r)
            fill = COLOR_C_WHITE if color == 'w' else COLOR_C_BLACK
            draw.ellipse([cx - checker_r, cy - checker_r, cx + checker_r, cy + checker_r], fill=fill, outline=COLOR_C_BLACK, width=1)
            text_str = str(n)
            bbox = draw.textbbox((0, 0), text_str, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            text_color = COLOR_C_BLACK if color == 'w' else COLOR_C_WHITE
            draw.text((cx - tw/2, cy - th/2), text_str, fill=text_color, font=font)
            continue

        if 1 <= point <= 6:
            cx, edge_y, direction = board_left + (point - 1 + 0.5) * px_point_base, board_bottom, -1
        elif 7 <= point <= 12:
            cx, edge_y, direction = bar_right + (point - 7 + 0.5) * px_point_base, board_bottom, -1
        elif 13 <= point <= 18:
            cx, edge_y, direction = bar_right + (18 - point + 0.5) * px_point_base, board_top, 1
        elif 19 <= point <= 24:
            cx, edge_y, direction = board_left + (24 - point + 0.5) * px_point_base, board_top, 1
        else: continue 
            
        for j in range(n):
            cy = edge_y + direction * (2 * checker_r * j + checker_r)
            fill = COLOR_C_WHITE if color == 'w' else COLOR_C_BLACK
            draw.ellipse([cx - checker_r, cy - checker_r, cx + checker_r, cy + checker_r], fill=fill, outline=COLOR_C_BLACK, width=1)
    
    return img.resize(canvas_size, Image.Resampling.LANCZOS)

# POSITION: 2w1 2b4 4b6 4b8 1b9 1b10 1w11 2w17 2w18 3w19 3w20 2w21 1b23 2b0
POSITION = [
    (1, 2, 'w'), (4, 2, 'b'), (6, 4, 'b'), (8, 4, 'b'), (9, 1, 'b'), 
    (10, 1, 'b'), (11, 1, 'w'), (17, 2, 'w'), (18, 2, 'w'), (19, 3, 'w'), 
    (20, 3, 'w'), (21, 2, 'w'), (23, 1, 'b'), (0, 2, 'b'),
]

OUT = "/Users/prh/Developer/huffmanwrites/static/img/articles"
os.makedirs(OUT, exist_ok=True)

l = generate(LANDSCAPE, POSITION)
p = generate(PORTRAIT, POSITION)
l.save(f"{OUT}/sb-order-disorder 16x9.png")
p.save(f"{OUT}/sb-order-disorder 4x5.png")
print("Saved sb-order-disorder 16x9.png + 4x5.png")
