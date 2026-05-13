#!/usr/bin/env python3
"""
Book Cover Generator Toolkit - "A Life Made Whole" Hardcover Edition
Visual: Kintsugi aesthetic (broken stone with gold veins).
Dimensions: 6" x 9" Trim, 136 Pages.
"""

import math
import random
import io
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class BookCoverGenerator:
    def __init__(self, page_count=136): 
        self.TRIM_W = 6.0
        self.TRIM_H = 9.0
        self.BLEED = 0.125
        self.DPI = 300
        self.PAGE_COUNT = page_count
        self.PAPER_THICKNESS = 0.0035

        self.spine = self.PAGE_COUNT * self.PAPER_THICKNESS
        self.total_w = 14.063 # Exact expected width from KDP context
        self.total_h = 10.417 # Exact expected height from KDP context

        self.W = int(round(self.total_w * self.DPI))
        self.H = int(round(self.total_h * self.DPI))

        self.bleed_px = int(round(self.BLEED * self.DPI))
        self.trim_w_px = int(round(self.TRIM_W * self.DPI))
        # Fixed logic below:
        self.trim_w_px = int(round(self.TRIM_W * self.DPI))
        self.trim_h_px = int(round(self.TRIM_H * self.DPI))
        self.spine_px = int(round(self.spine * self.DPI))

        # HC offsets (estimated based on the 14.063 width)
        self.back_left = self.bleed_px + int(0.375 * self.DPI)
        self.back_right = self.back_left + self.trim_w_px
        self.spine_left = self.back_right
        self.spine_right = self.spine_left + self.spine_px
        self.front_left = self.spine_right
        self.front_right = self.front_left + self.trim_w_px
        self.safe_margin = int(round(0.25 * self.DPI))

        self.colors = {
            'BG': (245, 245, 240),
            'GOLD': (184, 134, 11),
            'TEXT': (40, 40, 40),
            'STONE': [(220, 210, 200), (200, 190, 180), (180, 170, 160), (210, 200, 190)]
        }
        
        self.fonts = {
            'SERIF_BOLD': "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            'SERIF_ITALIC': "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
            'SANS': "/System/Library/Fonts/Supplemental/Arial.ttf"
        }
        
        self.author_bottom_margin = 0.75

    def _load_font(self, font_key, size):
        try:
            return ImageFont.truetype(self.fonts[font_key], size)
        except Exception:
            return ImageFont.load_default()

    def generate_kintsugi_layer(self, draw, region_x, region_y, region_w, region_h):
        num_shards = 25
        for _ in range(num_shards):
            center_x = random.randint(region_x, region_x + region_w)
            center_y = random.randint(region_y, region_y + region_h)
            shard_points = []
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(20, 120)
                shard_points.append((center_x + dist * math.cos(angle), center_y + dist * math.sin(angle)))
            color = random.choice(self.colors['STONE'])
            draw.polygon(shard_points, fill=color)
            draw.polygon(shard_points, outline=self.colors['GOLD'], width=2)

    def generate(self, output_png="life_made_whole_hc_cover.png", output_pdf="life_made_whole_hc_kdp.pdf"):
        img = Image.new("RGB", (self.W, self.H), self.colors['BG'])
        draw = ImageDraw.Draw(img)

        tex_y = int(self.H * 0.33)
        self.generate_kintsugi_layer(draw, 0, tex_y, self.W, self.H - tex_y)

        font_title = self._load_font('SERIF_BOLD', 120)
        font_subtitle = self._load_font('SERIF_ITALIC', 32)
        font_author = self._load_font('SANS', 36)
        
        title_text = "A LIFE MADE WHOLE"
        tb = draw.textbbox((0, 0), title_text, font=font_title)
        tw, th = tb[2]-tb[0], tb[3]-tb[1]
        tx = self.front_left + (self.trim_w_px - tw) // 2
        ty = self.bleed_px + int(1.2 * self.DPI)
        draw.text((tx, ty), title_text, font=font_title, fill=self.colors['TEXT'])

        subtitle_text = "Essays on Inner Strength and Resilience"
        sb = draw.textbbox((0, 0), subtitle_text, font=font_subtitle)
        sw, sh = sb[2]-sb[0], sb[3]-sb[1]
        sx = self.front_left + (self.trim_w_px - sw) // 2
        sy = ty + th + int(0.4 * self.DPI)
        draw.text((sx, sy), subtitle_text, font=font_subtitle, fill=self.colors['TEXT'])

        author_text = "PHILIP HUFFMAN"
        ab = draw.textbbox((0, 0), author_text, font=font_author)
        aw, ah = ab[2]-ab[0], ab[3]-ab[1]
        ax = self.front_left + (self.trim_w_px - aw) // 2
        ay = self.bleed_px + self.trim_h_px - int(self.author_bottom_margin * self.DPI) - ah
        draw.text((ax, ay), author_text, font=font_author, fill=self.colors['TEXT'])

        font_spine = self._load_font('SERIF_BOLD', 40)
        stb = draw.textbbox((0, 0), title_text, font=font_spine)
        stw, sth = stb[2]-stb[0], stb[3]-stb[1]
        st_img = Image.new("RGBA", (stw + 10, sth + 10), (0, 0, 0, 0))
        ImageDraw.Draw(st_img).text((5, 5), title_text, font=font_spine, fill=self.colors['TEXT'])
        st_img = st_img.rotate(270, expand=True)
        img.paste(st_img, (self.spine_left + (self.spine_px - st_img.width)//2, self.bleed_px + int(1.0 * self.DPI)), st_img)

        font_back = self._load_font('SANS', 32)
        blurb_text = ("A Life Made Whole examines the long process of integration — not the dramatic breakthroughs, but the daily work of holding together what experience threatens to fragment. The essays trace the Stoic virtues not as ideals to achieve, but as practices to maintain under pressure, loss, and the slow erosion of circumstance.\n\nIt argues that wholeness is not a state to reach but a direction to hold, maintained by small, repeated choices in the face of what cannot be controlled.")
        
        max_blurb_w = self.trim_w_px - self.safe_margin * 2
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

        bx = self.back_left + self.safe_margin
        by = self.bleed_px + int(1.5 * self.DPI)
        for i, line in enumerate(blurb_lines):
            draw.text((bx, by + i * int(0.4 * self.DPI)), line, font=font_back, fill=self.colors['TEXT'])

        bw, bh = int(2.0 * self.DPI), int(1.2 * self.DPI)
        b_x, b_y = self.back_right - self.safe_margin - bw, self.bleed_px + self.trim_h_px - self.safe_margin - bh
        draw.rectangle([(b_x, b_y), (b_x + bw, b_y + bh)], fill=(245, 245, 245), outline=(180, 180, 180), width=2)

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
    print("A Life Made Whole HC Cover generated successfully.")
