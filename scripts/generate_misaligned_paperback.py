#!/usr/bin/env python3
"""
Book Cover Generator Toolkit - "Misaligned" Paperback Edition
Theme: The experience of neurodivergence (Traveling with the wrong map).
Visual: Earth tones, shifted grids, and topographic dissonance.
Dimensions: 5" x 8" Trim, 185 Pages.
"""

import math
import random
import io
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class BookCoverGenerator:
    def __init__(self, page_count=185): 
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

        # --- Design Palette: Earth Tones ---
        self.colors = {
            'BG': (85, 76, 62),          # Deep Umber/Earth Brown
            'ACCENT': (184, 134, 11),   # Dark Goldenrod / Ochre
            'ACCENT_GLOW': (210, 180, 140), # Tan / Parchment glow
            'TEXT': (235, 230, 210),    # Soft Cream/Parchment
            'SUBTITLE': (160, 150, 130),# Muted Taupe
            'TEXT_DIM': (120, 110, 90)  # Dark Olive/Brown
        }
        
        self.fonts = {
            'TITLE': "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            'BOLD': "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            'REGULAR': "/System/Library/Fonts/Supplemental/Arial.ttf"
        }
        
        self.author_bottom_margin = 0.75
        self.author_font_size = 38 # Slightly smaller for 5x8 page

    def _load_font(self, font_key, size):
        try:
            return ImageFont.truetype(self.fonts[font_key], size)
        except Exception:
            return ImageFont.load_default()

    def generate(self, output_png="misaligned_paperback.png", output_pdf="misaligned_paperback_kdp.pdf"):
        img = Image.new("RGB", (self.W, self.H), self.colors['BG'])
        draw = ImageDraw.Draw(img)

        # --- Background: Black Grid and Topo Lines ---
        grid_spacing = int(0.75 * self.DPI)
        for x in range(0, self.W, grid_spacing):
            draw.line([x, 0, x, self.H], fill=(0, 0, 0), width=1)
        for y in range(0, self.H, grid_spacing):
            draw.line([0, y, self.W, y], fill=(0, 0, 0), width=1)

        line_count = 20
        for i in range(line_count):
            points = []
            seed = i * 150
            base_offset = (self.H // line_count) * i
            for px in range(0, self.W + 1, 100):
                amplitude = (self.H // line_count) // 3
                py = base_offset + math.sin(px * 0.005 + seed) * amplitude + math.cos(px * 0.002 + seed) * (amplitude // 2)
                points.append((px, py))
            draw.line(points, fill=(0, 0, 0), width=1)

        # --- The "Misaligned Area" (Rotated Box) ---
        warp_center_x = self.front_left + (self.trim_w_px // 2)
        warp_center_y = (self.H // 2) - int(0.125 * self.DPI)
        warp_w = int(2.0 * self.DPI)
        warp_h = int(4.0 * self.DPI)
        
        rect_img = Image.new("RGBA", (warp_w + 100, warp_h + 100), (0, 0, 0, 0))
        rect_draw = ImageDraw.Draw(rect_img)
        rect_draw.rectangle([50, 50, 50 + warp_w, 50 + warp_h], fill=self.colors['ACCENT'], outline=self.colors['ACCENT_GLOW'], width=3)
        
        rotated_rect = rect_img.rotate(3, resample=Image.BICUBIC, expand=True)
        paste_x = warp_center_x - rotated_rect.width // 2
        paste_y = warp_center_y - rotated_rect.height // 2
        img.paste(rotated_rect, (paste_x, paste_y), rotated_rect)
        
        # --- Text Layout ---
        font_title = self._load_font('TITLE', 140) # Scaled down for 5x8
        font_subtitle = self._load_font('BOLD', 34)
        font_author = self._load_font('BOLD', self.author_font_size)
        
        # Title
        title_text = "MISALIGNED"
        tb = draw.textbbox((0, 0), title_text, font=font_title)
        tw, th = tb[2]-tb[0], tb[3]-tb[1]
        tx = self.front_left + (self.trim_w_px - tw) // 2
        ty = self.bleed_px + int(1.5 * self.DPI)
        draw.text((tx, ty), title_text, font=font_title, fill=self.colors['TEXT'])

        # Subtitle (Rotated 3 deg)
        subtitle = "Right Subject\nWrong Adjective\nDisastrous Result"
        sub_lines = subtitle.split('\n')
        sub_img = Image.new("RGBA", (self.trim_w_px, int(3 * self.DPI)), (0, 0, 0, 0))
        sub_draw = ImageDraw.Draw(sub_img)
        
        curr_sub_y = int(0.2 * self.DPI)
        for line in sub_lines:
            sb = sub_draw.textbbox((0, 0), line, font=font_subtitle)
            sw = sb[2]-sb[0]
            sx = (self.trim_w_px - sw) // 2
            sub_draw.text((sx, curr_sub_y), line, font=font_subtitle, fill=(60, 50, 40))
            curr_sub_y += int(0.5 * self.DPI)

        rotated_sub = sub_img.rotate(3, resample=Image.BICUBIC, expand=True)
        sub_paste_x = self.front_left + (self.trim_w_px - rotated_sub.width) // 2
        sub_paste_y = ty + th + int(0.6 * self.DPI)
        img.paste(rotated_sub, (sub_paste_x, sub_paste_y), rotated_sub)

        # Author
        author = "PHILIP HUFFMAN"
        ab = draw.textbbox((0, 0), author, font=font_author)
        aw = ab[2]-ab[0]
        ax = self.front_left + (self.trim_w_px - aw) // 2
        ay = self.bleed_px + self.trim_h_px - int(self.author_bottom_margin * self.DPI) - ab[3]
        draw.text((ax, ay), author, font=font_author, fill=self.colors['TEXT_DIM'])

        # Spine
        font_spine = self._load_font('BOLD', 38) # Adjusted for smaller spine
        font_spine_small = self._load_font('REGULAR', 26)
        spine_title = "MISALIGNED"
        stb = draw.textbbox((0, 0), spine_title, font=font_spine)
        stw, sth = stb[2]-stb[0], stb[3]-stb[1]
        st_img = Image.new("RGBA", (stw + 10, sth + 10), (0, 0, 0, 0))
        ImageDraw.Draw(st_img).text((5, 5), spine_title, font=font_spine, fill=self.colors['TEXT'])
        st_img = st_img.rotate(270, expand=True)
        img.paste(st_img, (self.spine_left + (self.spine_px - st_img.width)//2, self.bleed_px + int(1.0 * self.DPI)), st_img)

        spine_auth = "PHILIP HUFFMAN"
        sab = draw.textbbox((0, 0), spine_auth, font=font_spine_small)
        saw, sah = sab[2]-sab[0], sab[3]-sab[1]
        sa_img = Image.new("RGBA", (saw + 10, sah + 10), (0, 0, 0, 0))
        ImageDraw.Draw(sa_img).text((5, 5), spine_auth, font=font_spine_small, fill=self.colors['ACCENT_GLOW'])
        sa_img = sa_img.rotate(270, expand=True)
        img.paste(sa_img, (self.spine_left + (self.spine_px - sa_img.width)//2, self.bleed_px + self.trim_h_px - sa_img.height - int(0.6 * self.DPI)), sa_img)

        # --- Back Cover Implementation ---
        font_size_back = 32
        color_text_back = self.colors['TEXT']
        line_spacing_back = int(0.3 * self.DPI)
        
        font_back = self._load_font('REGULAR', font_size_back)
        font_back_small = self._load_font('REGULAR', 20)
        font_quote = self._load_font('BOLD', 24)

        # Blurb
        max_blurb_w = self.trim_w_px - self.safe_margin * 2 - int(0.5 * self.DPI) 
        blurb_text = ("Misaligned is an exploration of the dissonant experience of navigating a neurotypical world with a neurodivergent mind. It is a study of the 'wrong map'—the internal blueprints that fail to align with external expectations, and the subsequent struggle to find a way home.\n\nThrough an examination of character, cognitive dissonance, and survival, it seeks to reconcile the gap between who we are told we should be and who we actually are, offering a path toward a more authentic self-governance.")
        
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

        blurb_x, blurb_y = self.back_left + self.safe_margin, self.bleed_px + int(1.1 * self.DPI) - int(0.75 * self.DPI)
        for i, line in enumerate(blurb_lines):
            draw.text((blurb_x, blurb_y + i * line_spacing_back), line, font=font_back, fill=color_text_back)
        
        # Quote logic for Misaligned
        quote = '"The only map that matters is the one that actually describes the terrain.'
        blurb_bottom = blurb_y + len(blurb_lines) * line_spacing_back
        qy = blurb_bottom + int(0.5 * self.DPI)
        draw.text((blurb_x, qy), quote, font=font_quote, fill=self.colors['ACCENT_GLOW'])

        # Author Photo
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
        except Exception as e:
            print(f"Could not load author photo: {e}")

        # Author Bio
        bio_text = (
            "Philip Huffman is a veteran of the United States Army, technologist, an "
            "essayist exploring the intersection of character and citizenship in "
            "modern America. Born in southern Illinois and raised in Springfield, he "
            "carries a Midwestern respect for responsibility and plain speech into "
            "both his life and his work. His service in the Army shaped his enduring "
            "interest in duty, leadership, and moral courage."
        )
        
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
        bio_y = self.bleed_px + (self.trim_h_px // 2) + int(1.0 * self.DPI) - int(0.5 * self.DPI)
        for i, line in enumerate(bio_lines):
            draw.text((bio_x, bio_y + i * line_spacing_back), line, font=font_back, fill=color_text_back)

        # Barcode
        barcode_w, barcode_h = int(2.0 * self.DPI), int(1.2 * self.DPI)
        barcode_x, barcode_y = self.back_right - self.safe_margin - barcode_w, self.bleed_px + self.trim_h_px - self.safe_margin - barcode_h
        draw.rectangle([(barcode_x, barcode_y), (barcode_x + barcode_w, barcode_y + barcode_h)], fill=(245, 245, 245), outline=(180, 180, 180), width=2)
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
    print("Misaligned Paperback Cover generated successfully.")
