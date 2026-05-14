#!/usr/bin/env python3
"""Generate a single standalone checker for a Stoic Backgammon asset."""
import os
from PIL import Image, ImageDraw, ImageFont

# Constants
SS = 4  # Supersampling
CANVAS_SIZE = (512, 512)
S_W, S_H = CANVAS_SIZE[0] * SS, CANVAS_SIZE[1] * SS

COLOR_BG = (5, 5, 30)          # Midnight Blue
COLOR_C_WHITE = (250, 235, 215) # Antique White
COLOR_C_BLACK = (0, 0, 0)       # Deep Black

def generate_checker(color='w'):
    img = Image.new('RGB', (S_W, S_H), COLOR_BG)
    draw = ImageDraw.Draw(img)
    
    # Center point
    cx, cy = S_W / 2, S_H / 2
    # Proportional radius (matching the board script's 0.45 unit * scale)
    # In a 512px canvas, we'll make it large and clear
    r = 150 * SS 
    
    fill = COLOR_C_WHITE if color == 'w' else COLOR_C_BLACK
    
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], 
                fill=fill, outline=COLOR_C_BLACK, width=2)
    
    return img.resize(CANVAS_SIZE, Image.Resampling.LANCZOS)

OUT = "/Users/prh/Developer/huffmanwrites/static/img/articles"
os.makedirs(OUT, exist_ok=True)

# Generate one of each
generate_checker(color='w').save(f"{OUT}/checker-white.png")
generate_checker(color='b').save(f"{OUT}/checker-black.png")

print("Saved checker-white.png and checker-black.png")
