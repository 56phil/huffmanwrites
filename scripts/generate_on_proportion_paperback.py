#!/usr/bin/env python3
"""
Book Cover Generator Toolkit - "On Proportion" Paperback Edition
Theme: The Cold War, Radar Screens, Electronic Surveillance.
Visual: Deep Navy, phosphor-green radar sweeps, concentric rings, and blips.
Dimensions: 5" x 8" Trim, 85 Pages, Paperback.
"""

import math
import random
import io
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class BookCoverGenerator:
    def __init__(self, page_count=113): 
        # --- Base Dimensions (Paperback 5x8) ---
        self.TRIM_W = 5.0
        self.TRIM_H = 8.0
        self.BLEED = 0.125
        self.DPI = 300
        self.PAGE_COUNT = page_count
        self.PAPER_THICKNESS = 0.002252

        self.spine = self.PAGE_COUNT * self.PAPER_THICKNESS
        self.total_w = self.TRIM_W * 2 + self.spine + self.BLEED * 2
        self.total_h = self.TRIM_H + self.BLEED * 2

        self.W = int(round(self.total_w * self.DPI))
        self.H = int(round(self.total_h * self.DPI))

        self.bleed_px = int(round(self.BLEED * self.DPI))
        self.trim_w_px = int(round(self.TRIM_W * self.DPI))
        self.trim_h_px = int(round(self.TRIM_H * self.DPI))
        self.spine_px = int(round(self.spine * self.DPI))

        self.back_left = self.bleed_px
        self.back_right = self.back_left + self.trim_w_px
        self.spine_left = self.back_right
        self.spine_right = self.spine_left + self.spine_px
        self.front_left = self.spine_right
        self.front_right = self.front_left + self.trim_w_px
        self.safe_margin = int(round(0.25 * self.DPI))

        # --- Design Palette: Cold War Radar ---
        self.colors = {
            'BG': (5, 15, 35),           # Deep Navy / Midnight
            'ACCENT': (51, 255, 51),    # Phosphor Green (Classic Radar)
            'ACCENT_GLOW': (100, 255, 100), # Brighter Green
            'TEXT': (200, 230, 200),    # Minty off-white
            'SUBTITLE': (100, 150, 100),# Muted Green
            'TEXT_DIM': (50, 80, 50)    # Deep Shadow Green
        }
        
        self.fonts = {
            'TITLE': "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            'BOLD': "/System/Library/Fonts/Supplemental/Arial Bold the.ttf", # Fixed potential typo in logic, using a standard approach
            'REGULAR': "/System/Library/Fonts/Supplemental/Arial.ttf"
        }
        # Standardizing font paths to ensure consistency
        self.fonts['BOLD'] = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        
        self.author_bottom_margin = 0.75
        self.author_font_size = 38 # Scaled for 5x8

    def _load_font(self, font_key, size):
        try:
            return ImageFont.truetype(self.fonts[font_key], size)
        except Exception:
            return ImageFont.load_default()

    def generate(self, output_png="on_proportion_paperback.png", output_pdf="on_proportion_paperback_kdp.pdf"):
        img = Image.new("RGB", (self.W, self.H), self.colors['BG'])
        draw = ImageDraw.Draw(img)

        # --- Visual Metaphor: The Radar Screen (Front Cover Only) ---
        centerX = self.front_left + (self.trim_w_px // 2)
        centerY = self.H // 2

        rings = [int(0.0*self.DPI), int(0.5*self.DPI), int(1.0*self.DPI), int(1.5*self.DPI), int(2.0*self.DPI)]
        max_r = rings[-1]
        for r in rings:
            draw.ellipse([centerX-r, centerY-r, centerX+r, centerY+r], outline=self.colors['TEXT_DIM'], width=1)
        
        draw.line([centerX, centerY - max_r, centerX, centerY + max_r], fill=self.colors['TEXT_DIM'], width=1)
        draw.line([centerX - max_r, centerY, centerX + max_r, centerY], fill=self.colors['TEXT_DIM'], width=1)

        angle = random.randint(0, 360)
        sweep_length = max_r
        rad = math.radians(angle)
        endX = centerX + sweep_length * math.cos(rad)
        endY = centerY + sweep_length * math.sin(rad)
        draw.line([centerX, centerY, endX, endY], fill=self.colors['ACCENT'], width=3)

        for side in ['West', 'East']:
            for i in range(25):
                if side == 'West':
                    bX = centerX - random.uniform(2.5 * self.DPI, 0.2 * self.DPI)
                    vertical_spread = 1.5 * self.DPI if bX < centerX - 1.5 * self.DPI else 0.8 * self.DPI
                    bY = centerY + random.uniform(-vertical_spread, vertical_spread)
                else:
                    bX = centerX + random.uniform(0.2 * self.DPI, 2.5 * self.DPI)
                    vertical_spread = 1.5 * self.DPI if bX > centerX + 1.5 * self.DPI else 0.8 * self.DPI
                    bY = centerY + random.uniform(-vertical_spread, vertical_spread)
                
                if math.hypot(bX - centerX, bY - centerY) <= max_r:
                    r_blip = random.randint(3, 7)
                    draw.ellipse([bX-r_blip, bY-r_blip, bX+r_blip, bY+r_blip], fill=self.colors['ACCENT'], outline=self.colors['ACCENT_GLOW'])

        # --- Text Layout (Adjusted for 5x8) ---
        font_title = self._load_font('TITLE', 140) 
        font_author = self._load_font('BOLD', self.author_font_size)
        
        title_text = "ON\nPROPORTION"
        lines = title_text.split('\n')
        curr_y = self.bleed_px + int(0.5 * self.DPI) - int(0.33 * self.DPI)
        for line in lines:
            tb = draw.textbbox((0, 0), line, font=font_title)
            tw, th = tb[2]-tb[0], tb[3]-tb[1]
            tx = self.front_left + (self.trim_w_px - tw) // 2
            draw.text((tx, curr_y), line, font=font_title, fill=self.colors['TEXT'])
            curr_y += th + 20

        author = "PHILIP HUFFMAN"
        ab = draw.textbbox((0, 0), author, font=font_author)
        aw = ab[2]-ab[0]
        ax = self.front_left + (self.trim_w_px - aw) // 2
        ay = self.bleed_px + self.trim_h_px - int(self.author_bottom_margin * self.DPI) - ab[3]
        draw.text((ax, ay), author, font=font_author, fill=self.colors['TEXT_DIM'])

        # Spine (Removed text as there is not enough room)
        pass

        # --- Back Cover ---
        font_size_back = 32 # Adjusted for 5" width
        color_text_back = self.colors['TEXT']
        line_spacing_back = int(0.3 * self.DPI)
        font_back = self._load_font('REGULAR', font_size_back)
        font_quote = self._load_font('BOLD', 24)

        max_blurb_w = self.trim_w_px - self.safe_margin * 2 - int(0.5 * self.DPI) 
        blurb_text = ("On Proportion examines the lost discipline of matching response to scale: knowing when a situation demands attention and when it demands inattention, when intervention is warranted and when silence is the better instrument.\n\nThe book treats proportion not as moderation but as judgment — the capacity to sense the true size of an event and to resist the distortions of urgency, outrage, and habit.")
        
        blurb_lines = []
        for paragraph in blurb_text.split('\n\n'):
            words = paragraph.replace('\n', ' ').split()
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if draw.textbbox((0, 0), test_line, font=font_back)[2] > max_blurb_w:
                    blurb_lines.append(current_line.strip())
                    current_line = word + " "
                else:
                    current_line = test_line
            blurb_lines.append(current_line.strip())
            blurb_lines.append("")

        blurb_x, blurb_y = self.back_left + self.safe_margin, self.bleed_px + int(1.1 * self.DPI) - int(0.5 * self.DPI)
        for i, line in enumerate(blurb_lines):
            draw.text((blurb_x, blurb_y + i * line_spacing_back), line, font=font_back, fill=color_text_back)

        quote = '"It was October 1962. I was six. The map appeared in the newspaper without emphasis.'
        blurb_bottom = blurb_y + len(blurb_lines) * line_spacing_back
        qy = blurb_bottom + int(0.5 * self.DPI) - int(0.33 * self.DPI)
        draw.text((blurb_x, qy), quote, font=font_quote, fill=self.colors['ACCENT_GLOW'])

        try:
            photo_path = "/Users/prh/texmf/tex/latex/miscImages/cPhilHuffman.jpg"
            photo = Image.open(photo_path)
            photo_size = int(1.5 * self.DPI)
            photo = photo.convert("RGB")
            w, h = photo.size
            min_dim = min(w, h)
            left = (w - min_dim) / 2
            top = (h - min_dim) / 2
            photo = photo.crop((left, top, left + min_dim, top + min_dim))
            photo = photo.resize((photo_size, photo_size), Image.LANCZOS)
            px = self.back_left + self.safe_margin
            py = self.bleed_px + self.trim_h_px - photo_size - self.safe_margin
            img.paste(photo, (px, py))
        except Exception:
            pass

        bio_text = ("Philip Huffman is a veteran of the United States Army, technologist, an "
            "essayist exploring the intersection of character and citizenship in "
            "modern America. Born in southern Illinois and raised in Springfield, he "
            "carries a Midwestern respect for responsibility and plain speech into "
            "both his life and his work. His service in the Army shaped his enduring "
            "interest in duty, leadership, and moral courage.")
        
        bio_lines = []
        words = bio_text.split()
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if draw.textbbox((0, 0), test_line, font=font_back)[2] > max_blurb_w:
                bio_lines.append(current_line.strip())
                current_line = word + " "
            else:
                current_line = test_line
        bio_lines.append(current_line.strip())

        bio_x = blurb_x
        bio_y = self.bleed_px + (self.trim_h_px // 2) + int(1.0 * self.DPI) - int(0.67 * self.DPI)
        for i, line in enumerate(bio_lines):
            draw.text((bio_x, bio_y + i * line_spacing_back), line, font=font_back, fill=color_text_back)

        barcode_w, barcode_h = int(2.0 * self.DPI), int(1.2 * self.DPI)
        barcode_x, barcode_y = self.back_right - self.safe_margin - barcode_w, self.bleed_px + self.trim_h_px - self.safe_margin - barcode_h
        draw.rectangle([(barcode_x, barcode_y), (barcode_x + barcode_w, barcode_y + barcode_h)], fill=(245, 245, 245), outline=(180, 180, 180), width=2)

        img.save(output_png, "PNG")
        pdf_w, pdf_h = self.total_w * 72, self.total_h * 72
        buf = io.BytesIO()
        img.save(buf, format="PNG", dpi=(self.DPI, self.DPI))
        buf.seek(0)
        c = canvas.Canvas(output_pdf, pagesize=(pdf_w, pdf_h))
        c.drawImage(ImageReader(buf), 0, 0, width=pdf_w, height=pdf_h)
        c.save()
        return output_png

if __name__ == "__main__":
    gen = BookCoverGenerator()
    gen.generate()
    print("On Proportion Paperback Cover generated successfully.")
