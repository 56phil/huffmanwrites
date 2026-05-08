#!/usr/bin/env python3
"""
Book Cover Generator Toolkit - "The Stoic CGM" Edition
Focus: Metabolic data, Stoic self-governance, and the 'Republic of Glucose'.
"""

import math
import random
import io
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

class BookCoverGenerator:
    def __init__(self, page_count=120): # Adjusted for a typical full-length guide
        # --- Base Dimensions ---
        self.TRIM_W = 6.0
        self.TRIM_H = 9.0
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

        # --- Design Palette: Clinical yet Philosophical ---
        # Moving from "Dark/Amber" to "Slate/Medical Blue/Silver"
        # Theme: Precision, Calm, Data, Governance.
        self.colors = {
            'BG': (28, 34, 42),         # Deep slate blue-grey
            'ACCENT': (0, 191, 255),    # Deep sky blue (medical precision/tech)
            'ACCENT_GLOW': (173, 216, 230), # Light blue glow
            'TEXT': (240, 240, 240),    # Off-white
            'SUBTITLE': (200, 200, 200),# Silver/Grey
            'TEXT_DIM': (150, 160, 170) # Steel grey
        }
        
        self.fonts = {
            'TITLE': "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            'BOLD': "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            'REGULAR': "/System/Library/Fonts/Supplemental/Arial.ttf"
        }

        # --- Design Parameters ---
        # Controlled range: staying within a healthy bandwidth while trending slightly lower
        # y values: Lower number = higher on page. 
        # Healthy Range: 4.0" to 6.0" from top.
        self.curve_points = [
            ('back', 0.5, 4.2, 4),
            ('back', 1.0, 4.1, 6),
            ('back', 1.5, 4.3, 8),
            ('back', 2.0, 4.0, 10),
            ('back', 2.5, 4.2, 12),
            ('back', 3.0, 4.4, 12),
            ('back', 3.5, 4.1, 12),
            ('back', 4.0, 4.3, 12),
            ('back', 4.5, 4.0, 12),
            ('back', 5.0, 4.2, 12),
            ('back', 5.5, 4.1, 12),
            ('spine', 0.3, 4.5, 15), 
            ('spine', 0.6, 4.6, 18),
            ('spine', 0.9, 4.4, 20),
            ('front', 0.5, 4.7, 30),
            ('front', 1.0, 4.6, 35),
            ('front', 1.5, 4.9, 35),
            ('front', 2.0, 4.7, 40),
            ('front', 2.5, 5.1, 40),
            ('front', 3.0, 4.8, 60), 
            ('front', 3.5, 5.2, 40),
            ('front', 4.0, 4.9, 40),
            ('front', 4.5, 5.3, 30),
            ('front', 5.0, 5.1, 30),
            ('front', 5.5, 5.4, 25),
            ('front', 6.0, 5.6, 20), # Lowest point, but still within healthy range (closer to bottom than start)
        ]
        
        self.author_bottom_margin = 0.75
        self.author_font_size = 42

    def _load_font(self, font_key, size):
        try:
            return ImageFont.truetype(self.fonts[font_key], size)
        except Exception:
            return ImageFont.load_default()

    def _calculate_curve_coords(self):
        pts = []
        for section, x_off, y_in, w in self.curve_points:
            if section == 'back':
                x = self.back_left + (x_off * self.DPI)
            elif section == 'spine':
                x = self.spine_left + (x_off * self.spine_px) if x_off < 1.0 else self.spine_right
            else:
                x = self.front_left + (x_off * self.DPI)
            y = int(y_in * self.DPI)
            pts.append((x, y, w))
        return pts

    def generate(self, output_png="stoic_cgm_cover.png", output_pdf="stoic_cgm_kdp.pdf"):
        img = Image.new("RGB", (self.W, self.H), self.colors['BG'])
        draw = ImageDraw.Draw(img)

        # Subtle gradient effect: slightly lighter in the center
        # (Simulation: we'll skip noise for a cleaner 'clinical' look)

        curve_pts = self._calculate_curve_coords()
        
        left_edge, right_edge = [], []
        for i in range(len(curve_pts)):
            x, y, w = curve_pts[i]
            px, py = (curve_pts[i-1][0], curve_pts[i-1][1]) if i > 0 else (x, y)
            nx, ny = (curve_pts[i+1][0], curve_pts[i+1][1]) if i < len(curve_pts)-1 else (x, y)
            dx = (nx - px) / 2 if not (i == 0 or i == len(curve_pts)-1) else (nx-x if i==0 else x-px)
            dy = (ny - py) / 2 if not (i == 0 or i == len(curve_pts)-1) else (ny-y if i==0 else y-py)
            length = math.hypot(dx, dy) or 1
            perp_x, perp_y = -dy / length, dx / length
            
            # Less jagged than 'Unstuck', more like a smooth medical trace
            jag = random.uniform(-0.02, 0.02) * w
            left_edge.append((x + perp_x * (w/2 + jag), y + perp_y * (w/2 + jag)))
            right_edge.append((x - perp_x * (w/2 + jag), y - perp_y * (w/2 + jag)))

        # Render the 'Data Wave'
        inner_scale = 0.3
        ileft, iright = [], []
        for i in range(len(curve_pts)):
            x, y, w = curve_pts[i]
            px, py = (curve_pts[i-1][0], curve_pts[i-1][1]) if i > 0 else (x, y)
            nx, ny = (curve_pts[i+1][0], curve_pts[i+1][1]) if i < len(curve_pts)-1 else (x, y)
            dx = (nx - px) / 2 if not (i == 0 or i == len(curve_pts)-1) else (nx-x if i==0 else x-px)
            dy = (ny - py) / 2 if not (i == 0 or i == len(curve_pts)-1) else (ny-y if i==0 else y-py)
            length = math.hypot(dx, dy) or 1
            perp_x, perp_y = -dy / length, dx / length
            ileft.append((x + perp_x * w * inner_scale * 0.5, y + perp_y * w * inner_scale * 0.5))
            iright.append((x - perp_x * w * inner_scale * 0.5, y - perp_y * w * inner_scale * 0.5))

        for scale, color in [(0.7, (0, 100, 150)), (0.85, (0, 70, 120))]:
            oleft, oright = [], []
            for i in range(len(curve_pts)):
                x, y, w = curve_pts[i]
                px, py = (curve_pts[i-1][0], curve_pts[i-1][1]) if i > 0 else (x, y)
                nx, ny = (curve_pts[i+1][0], curve_pts[i+1][1]) if i < len(curve_pts)-1 else (x, y)
                dx = (nx - px) / 2 if not (i == 0 or i == len(curve_pts)-1) else (nx-x if i==0 else x-px)
                dy = (ny - py) / 2 if not (i == 0 or i == len(curve_pts)-1) else (ny-y if i==0 else y-py)
                length = math.hypot(dx, dy) or 1
                perp_x, perp_y = -dy / length, dx / length
                oleft.append((x + perp_x * w * scale * 0.5, y + perp_y * w * scale * 0.5))
                oright.append((x - perp_x * w * scale * 0.5, y - perp_y * w * scale * 0.5))
            draw.polygon(oleft + list(reversed(oright)), fill=color)

        draw.polygon(left_edge + list(reversed(right_edge)), fill=self.colors['ACCENT'])
        draw.polygon(ileft + list(reversed(iright)), fill=self.colors['ACCENT_GLOW'])

        # --- Text ---
        font_title = self._load_font('TITLE', 180) # Slightly smaller to fit the longer title
        font_subtitle = self._load_font('BOLD', 40)
        font_author = self._load_font('BOLD', self.author_font_size)
        
        # Title
        title_text = "THE STOIC\nCGM"
        lines = title_text.split('\n')
        curr_y = self.bleed_px + int(1.5 * self.DPI)
        for line in lines:
            tb = draw.textbbox((0, 0), line, font=font_title)
            tw, th = tb[2]-tb[0], tb[3]-tb[1]
            tx = self.front_left + (self.trim_w_px - tw) // 2
            for ox, oy in [(4, 4), (2, 2)]:
                draw.text((tx + ox, curr_y + oy), line, font=font_title, fill=(0, 0, 0))
            draw.text((tx, curr_y), line, font=font_title, fill=self.colors['TEXT'])
            curr_y += th + 20

        # Subtitle
        subtitle = "A Data-Driven Guide to\nReinventing Yourself After Sixty"
        sub_lines = subtitle.split('\n')
        for i, line in enumerate(sub_lines):
            lb = draw.textbbox((0, 0), line, font=font_subtitle)
            lw = lb[2]-lb[0]
            lx = self.front_left + (self.trim_w_px - lw) // 2
            ly = curr_y + int(0.6 * self.DPI) + i * int(0.25 * self.DPI)
            draw.text((lx, ly), line, font=font_subtitle, fill=self.colors['SUBTITLE'])

        # Author
        author = "PHILIP HUFFMAN"
        ab = draw.textbbox((0, 0), author, font=font_author)
        aw = ab[2]-ab[0]
        ax = self.front_left + (self.trim_w_px - aw) // 2
        ay = self.bleed_px + self.trim_h_px - int(self.author_bottom_margin * self.DPI) - ab[3]
        draw.text((ax, ay), author, font=font_author, fill=self.colors['TEXT_DIM'])

        # SPINE/BACK (kept consistent with previous layouts but themed)
        font_spine = self._load_font('BOLD', 44)
        font_spine_small = self._load_font('REGULAR', 30)
        spine_title = "THE STOIC CGM"
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

        # Unified Back Cover Text Settings
        font_size_back = 36
        color_text_back = self.colors['TEXT']
        line_spacing_back = int(0.32 * self.DPI)
        
        font_back = self._load_font('REGULAR', font_size_back)
        font_back_small = self._load_font('REGULAR', 20)
        font_quote = self._load_font('BOLD', 24)

        # Wrap blurb with safe margin relative to spine
        max_blurb_w = self.trim_w_px - self.safe_margin * 2 - int(0.5 * self.DPI) 
        blurb_text = ("The Stoic CGM treats continuous glucose monitoring as a practice of self-knowledge — not merely a medical intervention, but a discipline of attention applied to the body\u2019s own politics.\n\nIt examines what happens when Stoic principles meet metabolic data: how to respond to information without being ruled by it, and how to govern the self when the self is constantly in motion.\n\nWritten for those managing chronic conditions, aging metabolisms, or a simple desire to understand their bodies, this framework offers the path to genuine self-governance.")
        
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
            # Use a smaller gap for paragraph breaks to save space
            blurb_lines.append("") 

        blurb_x, blurb_y = self.back_left + self.safe_margin, self.bleed_px + int(1.1 * self.DPI)
        for i, line in enumerate(blurb_lines):
            draw.text((blurb_x, blurb_y + i * line_spacing_back), line, font=font_back, fill=color_text_back)
        
        # Calculate where blurb ends to place quote below it
        blurb_bottom = blurb_y + len(blurb_lines) * line_spacing_back
        
        quote = '"The body is not an enemy to defeat but a system to comprehend.'
        # Position quote below blurb, but leave space for the polygon
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
        bio_y = self.bleed_px + (self.trim_h_px // 2) + int(1.0 * self.DPI)
        
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
    print("Stoic CGM Cover generated successfully.")
