#!/usr/bin/env python3
"""
Book Cover Generator Toolkit
Allows for iterative adjustments to the "Unstuck" cover design.
"""

import math
import random
import io
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class BookCoverGenerator:
    def __init__(self, page_count=81):
        # --- Base Dimensions ---
        self.TRIM_W = 6.0
        self.TRIM_H = 9.0
        self.BLEED = 0.125
        self.DPI = 300
        self.PAGE_COUNT = page_count
        self.PAPER_THICKNESS = 0.002252 # KDP white paper

        self.spine = self.PAGE_COUNT * self.PAPER_THICKNESS
        self.total_w = self.TRIM_W * 2 + self.spine + self.BLEED * 2
        self.total_h = self.TRIM_H + self.BLEED * 2

        self.W = int(round(self.total_w * self.DPI))
        self.H = int(round(self.total_h * self.DPI))

        self.bleed_px = int(round(self.BLEED * self.DPI))
        self.trim_w_px = int(round(self.TRIM_W * self.DPI))
        self.trim_h_px = int(round(self.TRIM_H * self.DPI))
        self.spine_px = int(round(self.spine * self.DPI))

        # Coordinates
        self.back_left = self.bleed_px
        self.back_right = self.back_left + self.trim_w_px
        self.spine_left = self.back_right
        self.spine_right = self.spine_left + self.spine_px
        self.front_left = self.spine_right
        self.front_right = self.front_left + self.trim_w_px
        self.safe_margin = int(round(0.25 * self.DPI))

        # --- Default Styling ---
        self.colors = {
            'BG': (18, 18, 20),
            'ACCENT': (255, 130, 0),       # vivid amber
            'ACCENT_GLOW': (255, 200, 120), # warm gold
            'TEXT': (245, 245, 245),
            'SUBTITLE': (0, 255, 255),     # electric cyan
            'TEXT_DIM': (180, 180, 185)
        }
        
        self.fonts = {
            'TITLE': "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            'BOLD': "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            'REGULAR': "/System/Library/Fonts/Supplemental/Arial.ttf"
        }

        # --- Design Parameters (Iterative) ---
        # Crack points: (x_offset, y_inches, width)
        # Note: x_offset is relative to the section's left edge
        self.crack_points = [
            ('back', 1.0, 8.85, 6),
            ('back', 2.5, 8.45, 10),
            ('spine', 0.33, 7.25, 20), # spine 33% in
            ('spine', 1.0, 5.75, 45),   # spine right edge
            ('front', 1.0, 4.85, 140),
            ('front', 3.0, 4.05, 260),
            ('front', 5.2, 3.25, 180),
            ('front', 5.4, 0.0, 120),   # Extended to top right edge
        ]
        
        self.author_bottom_margin = 0.75 # inches
        self.author_font_size = 42

    def _load_font(self, font_key, size):
        try:
            return ImageFont.truetype(self.fonts[font_key], size)
        except Exception:
            return ImageFont.load_default()

    def _calculate_crack_coords(self):
        pts = []
        for section, x_off, y_in, w in self.crack_points:
            if section == 'back':
                x = self.back_left + (x_off * self.DPI)
            elif section == 'spine':
                # x_off here is treated as percentage of spine for simpler control
                x = self.spine_left + (x_off * self.spine_px) if x_off < 1.0 else self.spine_right
            else: # front
                x = self.front_left + (x_off * self.DPI)
            
            y = int(y_in * self.DPI)
            pts.append((x, y, w))
        return pts

    def generate(self, output_png="unstuck_cover_v2.png", output_pdf="unstuck_cover_kdp.pdf"):
        img = Image.new("RGB", (self.W, self.H), self.colors['BG'])
        draw = ImageDraw.Draw(img)

        # Background noise
        random.seed(42)
        pixels = img.load()
        for _ in range(80000):
            x = random.randint(0, self.W-1)
            y = random.randint(0, self.H-1)
            r, g, b = pixels[x, y]
            delta = random.randint(-10, 10)
            pixels[x, y] = (max(0, min(255, r+delta)), max(0, min(255, g+delta)), max(0, min(255, b+delta)))

        crack_pts = self._calculate_crack_coords()
        
        # Build polygon edges
        left_edge = []
        right_edge = []
        for i in range(len(crack_pts)):
            x, y, w = crack_pts[i]
            px, py = (crack_pts[i-1][0], crack_pts[i-1][1]) if i > 0 else (x, y)
            nx, ny = (crack_pts[i+1][0], crack_pts[i+1][1]) if i < len(crack_pts)-1 else (x, y)
            
            dx = (nx - px) / 2 if not (i == 0 or i == len(crack_pts)-1) else (nx-x if i==0 else x-px)
            dy = (ny - py) / 2 if not (i == 0 or i == len(crack_pts)-1) else (ny-y if i==0 else y-py)
            length = math.hypot(dx, dy) or 1
            perp_x, perp_y = -dy / length, dx / length
            
            jag = random.uniform(-0.12, 0.12) * w
            left_edge.append((x + perp_x * (w/2 + jag), y + perp_y * (w/2 + jag)))
            right_edge.append((x - perp_x * (w/2 + jag), y - perp_y * (w/2 + jag)))

        # Draw glow/main
        inner_scale = 0.35
        ileft, iright = [], []
        for i in range(len(crack_pts)):
            x, y, w = crack_pts[i]
            px, py = (crack_pts[i-1][0], crack_pts[i-1][1]) if i > 0 else (x, y)
            nx, ny = (crack_pts[i+1][0], crack_pts[i+1][1]) if i < len(crack_pts)-1 else (x, y)
            dx = (nx - px) / 2 if not (i == 0 or i == len(crack_pts)-1) else (nx-x if i==0 else x-px)
            dy = (ny - py) / 2 if not (i == 0 or i == len(crack_pts)-1) else (ny-y if i==0 else y-py)
            length = math.hypot(dx, dy) or 1
            perp_x, perp_y = -dy / length, dx / length
            ileft.append((x + perp_x * w * inner_scale * 0.5, y + perp_y * w * inner_scale * 0.5))
            iright.append((x - perp_x * w * inner_scale * 0.5, y - perp_y * w * inner_scale * 0.5))

        # Render layers
        for scale, color in [(0.7, (200, 100, 20)), (0.85, (140, 70, 15))]:
            oleft, oright = [], []
            for i in range(len(crack_pts)):
                x, y, w = crack_pts[i]
                px, py = (crack_pts[i-1][0], crack_pts[i-1][1]) if i > 0 else (x, y)
                nx, ny = (crack_pts[i+1][0], crack_pts[i+1][1]) if i < len(crack_pts)-1 else (x, y)
                dx = (nx - px) / 2 if not (i == 0 or i == len(crack_pts)-1) else (nx-x if i==0 else x-px)
                dy = (ny - py) / 2 if not (i == 0 or i == len(crack_pts)-1) else (ny-y if i==0 else y-py)
                length = math.hypot(dx, dy) or 1
                perp_x, perp_y = -dy / length, dx / length
                oleft.append((x + perp_x * w * scale * 0.5, y + perp_y * w * scale * 0.5))
                oright.append((x - perp_x * w * scale * 0.5, y - perp_y * w * scale * 0.5))
            draw.polygon(oleft + list(reversed(oright)), fill=color)

        draw.polygon(left_edge + list(reversed(right_edge)), fill=self.colors['ACCENT'])
        draw.polygon(ileft + list(reversed(iright)), fill=self.colors['ACCENT_GLOW'])

        # --- Text ---
        font_title = self._load_font('TITLE', 240)
        font_subtitle = self._load_font('BOLD', 44)
        font_author = self._load_font('BOLD', self.author_font_size)
        
        # Title
        title_text = "UNSTUCK"
        tb = draw.textbbox((0, 0), title_text, font=font_title)
        tw, th = tb[2]-tb[0], tb[3]-tb[1]
        title_x = self.front_left + (self.trim_w_px - tw) // 2
        title_y = self.bleed_px + int(1.35 * self.DPI)
        for ox, oy in [(4, 4), (2, 2)]:
            draw.text((title_x + ox, title_y + oy), title_text, font=font_title, fill=(0, 0, 0))
        draw.text((title_x, title_y), title_text, font=font_title, fill=self.colors['TEXT'])

        # Subtitle
        subtitle = "Brutal Guidance for Getting Out of\nYour Own Way"
        lines = subtitle.split('\n')
        for i, line in enumerate(lines):
            lb = draw.textbbox((0, 0), line, font=font_subtitle)
            lw = lb[2]-lb[0]
            lx = self.front_left + (self.trim_w_px - lw) // 2
            ly = title_y + th + int(0.45 * self.DPI) + i * int(0.18 * self.DPI)
            draw.text((lx, ly), line, font=font_subtitle, fill=self.colors['SUBTITLE'])

        # Author
        author = "PHILIP HUFFMAN"
        ab = draw.textbbox((0, 0), author, font=font_author)
        aw = ab[2]-ab[0]
        ax = self.front_left + (self.trim_w_px - aw) // 2
        ay = self.bleed_px + self.trim_h_px - int(self.author_bottom_margin * self.DPI) - ab[3]
        draw.text((ax, ay), author, font=font_author, fill=self.colors['TEXT_DIM'])

        # Spine/Back (simplified for brevity in refactor, but kept identical to v2)
        # [The spine and back cover logic from v2 remains exactly the same here]
        # ... (I'll omit the spine/back for this prompt response to keep it clean, 
        # but in the actual file I will include the full layout from v2) ...
        
        # Since I'm replacing the whole file, I should ensure SPINE and BACK are kept.
        # I will integrate the full v2 back/spine logic into the class.

        # SPINE logic
        font_spine = self._load_font('BOLD', 48)
        font_spine_small = self._load_font('REGULAR', 34)
        spine_title = "UNSTUCK"
        stb = draw.textbbox((0, 0), spine_title, font=font_spine)
        stw, sth = stb[2]-stb[0], stb[3]-stb[1]
        st_img = Image.new("RGBA", (stw + 10, sth + 10), (0, 0, 0, 0))
        ImageDraw.Draw(st_img).text((5, 5), spine_title, font=font_spine, fill=self.colors['TEXT'])
        st_img = st_img.rotate(270, expand=True)
        img.paste(st_img, (self.spine_left + (self.spine_px - st_img.width)//2, self.bleed_px + int(0.9 * self.DPI)), st_img)

        spine_auth = "PHILIP HUFFMAN"
        sab = draw.textbbox((0, 0), spine_auth, font=font_spine_small)
        saw, sah = sab[2]-sab[0], sab[3]-sab[1]
        sa_img = Image.new("RGBA", (saw + 10, sah + 10), (0, 0, 0, 0))
        ImageDraw.Draw(sa_img).text((5, 5), spine_auth, font=font_spine_small, fill=self.colors['ACCENT_GLOW'])
        sa_img = sa_img.rotate(270, expand=True)
        img.paste(sa_img, (self.spine_left + (self.spine_px - sa_img.width)//2, self.bleed_px + self.trim_h_px - sa_img.height - int(0.6 * self.DPI)), sa_img)

        # BACK logic
        font_back = self._load_font('REGULAR', 30)
        font_back_small = self._load_font('REGULAR', 22)
        font_quote = self._load_font('BOLD', 26)
        blurb = ("Most obstacles are not external.\nThey are internal negotiations\nwe have learned to accept.\n\nUNSTUCK rejects motivational fluff\nand insists on discipline, responsibility,\nand daily action.\n\nDrawing on Stoic wisdom, it argues that\nthe right response to uncertainty is not\nprediction—but character.\n\nStop waiting. Move now.")
        blurb_x, blurb_y = self.back_left + self.safe_margin, self.bleed_px + int(1.1 * self.DPI)
        for i, line in enumerate(blurb.split('\n')):
            draw.text((blurb_x, blurb_y + i * int(0.2 * self.DPI)), line, font=font_back, fill=self.colors['TEXT'])
        
        quote = '"The happiness of your life depends upon\nthe quality of your thoughts."\n— Marcus Aurelius'
        qy = self.bleed_px + self.trim_h_px - self.safe_margin - int(1.8 * self.DPI)
        for i, line in enumerate(quote.split('\n')):
            draw.text((blurb_x, qy + i * int(0.16 * self.DPI)), line, font=font_quote, fill=self.colors['ACCENT_GLOW'])

        principles = "1. Stop Stalling   2. Your Excuses Are BS   3. Embrace Discomfort   4. Don\u2019t Negotiate\n5. Action Comes First   6. Stack Wins   7. Persistence Over Perfection   8. Don\u2019t Miss Twice"
        words = principles.replace('\n', ' ').split()
        max_w = self.trim_w_px - self.safe_margin * 2
        line, line_idx, pr_y = "", 0, qy - int(0.5 * self.DPI)
        for word in words:
            test = line + word + "  "
            tb = draw.textbbox((0, 0), test, font=font_back_small)
            if (tb[2] - tb[0]) > max_w and line:
                draw.text((blurb_x, pr_y + line_idx * int(0.14 * self.DPI)), line.strip(), font=font_back_small, fill=self.colors['TEXT_DIM'])
                line, line_idx = word + "  ", line_idx + 1
            else: line = test
        draw.text((blurb_x, pr_y + line_idx * int(0.14 * self.DPI)), line.strip(), font=font_back_small, fill=self.colors['TEXT_DIM'])

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
    print("Cover generated successfully.")
