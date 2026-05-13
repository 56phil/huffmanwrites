#!/usr/bin/env python3
"""
Book Cover Generator Toolkit - "The Stoic Citizen" Hardcover Edition
Dimensions: 6" x 9" Trim, 136 Pages.
"""

import math
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
        self.PAPER_THICKNESS = 0.0035 # Increased for HC

        self.spine = self.PAGE_COUNT * self.PAPER_THICKNESS
        self.total_w = 14.063 # Exact expected width in inches
        self.total_h = 10.417 # Exact expected height in inches

        self.W = int(round(self.total_w * self.DPI))
        self.H = int(round(self.total_h * self.DPI))

        self.bleed_px = int(round(self.BLEED * self.DPI))
        self.trim_w_px = int(round(self.TRIM_W * self.DPI))
        self.trim_h_px = int(round(self.TRIM_H * self.DPI))
        self.spine_px = int(round(self.spine * self.DPI))

        self.back_left = self.bleed_px + int(0.375 * self.DPI) # offset for board wrap
        self.back_right = self.back_left + self.trim_w_px
        self.spine_left = self.back_right
        self.spine_right = self.spine_left + self.spine_px
        self.front_left = self.spine_right
        self.front_right = self.front_left + self.trim_w_px
        self.safe_margin = int(round(0.25 * self.DPI))

        self.colors = {
            'BG': (20, 30, 50),
            'GOLD': (184, 134, 11),
            'GOLD_LIGHT': (218, 165, 32),
            'TEXT': (245, 245, 240),
            'TEXT_DIM': (160, 170, 190)
        }
        
        self.fonts = {
            'TITLE': "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            'BOLD': "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            'REGULAR': "/System/Library/Fonts/Supplemental/Arial.ttf"
        }
        
        self.author_bottom_margin = 0.75
        self.author_font_size = 42

    def _load_font(self, font_key, size):
        try:
            return ImageFont.truetype(self.fonts[font_key], size)
        except Exception:
            return ImageFont.load_default()

    def generate(self, output_png="stoic_citizen_hc_cover.png", output_pdf="stoic_citizen_hc_kdp.pdf"):
        img = Image.new("RGB", (self.W, self.H), self.colors['BG'])
        draw = ImageDraw.Draw(img)

        virtues = [
            ("WISDOM", "Top Left"),
            ("JUSTICE", "Top Right"),
            ("COURAGE", "Bottom Left"),
            ("TEMPERANCE", "Bottom Right")
        ]
        
        font_virtue = self._load_font('TITLE', 48)
        v_margin = int(0.6 * self.DPI)
        
        v_coords = [
            (self.front_left + v_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.2 * self.DPI) + int(0.2 * self.DPI) - int(0.1 * self.DPI) - int(0.05 * self.DPI), self.bleed_px + v_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.3 * self.DPI) + int(0.4 * self.DPI) - int(0.2 * self.DPI)),
            (self.front_right - v_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.2 * self.DPI) + int(0.2 * self.DPI) - int(0.1 * self.DPI) - int(0.05 * self.DPI), self.bleed_px + v_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.3 * self.DPI) + int(0.4 * self.DPI) - int(0.2 * self.DPI)),
            (self.front_left + v_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.2 * self.DPI) + int(0.2 * self.DPI) - int(0.1 * self.DPI) - int(0.05 * self.DPI), self.bleed_px + self.trim_h_px - v_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.3 * self.DPI) + int(0.4 * self.DPI) - int(0.2 * self.DPI)),
            (self.front_right - v_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.2 * self.DPI) + int(0.2 * self.DPI) - int(0.1 * self.DPI) - int(0.05 * self.DPI), self.bleed_px + self.trim_h_px - v_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.3 * self.DPI) + int(0.4 * self.DPI) - int(0.2 * self.DPI)),
        ]
        
        for i, (text, pos) in enumerate(virtues):
            vb = draw.textbbox((0, 0), text, font=font_virtue)
            vw, vh = vb[2] - vb[0], vb[3] - vb[1]
            cx, cy = v_coords[i]
            rotation = 45
            if text == "WISDOM" or text == "TEMPERANCE":
                rotation = -45
            if text == "COURAGE":
                cx += int(0.30 * self.DPI)
                cy -= int(0.4 * self.DPI)
            elif text == "JUSTICE":
                cx -= int(0.36 * self.DPI)
                cy += int(0.275 * self.DPI)
            elif text == "WISDOM":
                rotation = -45
                cx += int(0.275 * self.DPI)
                cy += int(0.20 * self.DPI)
            elif text == "TEMPERANCE":
                rotation = -45
                cx -= int(0.44 * self.DPI)
                cy -= int(0.532 * self.DPI)

            padding = 100
            txt_img = Image.new("RGBA", (vw + padding, vh + padding), (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((padding//2, padding//2), text, font=font_virtue, fill=self.colors['GOLD'])
            rotated_txt = txt_img.rotate(rotation, expand=True, resample=Image.BICUBIC)
            paste_x = cx - rotated_txt.width // 2
            paste_y = cy - rotated_txt.height // 2
            img.paste(rotated_txt, (paste_x, paste_y), rotated_txt)

        border_w = int(0.06 * self.DPI)
        frame_margin = int(0.4 * self.DPI)
        f_l, f_t = self.front_left + frame_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.2 * self.DPI) + int(0.2 * self.DPI) - int(0.1 * self.DPI) - int(0.05 * self.DPI), self.bleed_px + frame_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.3 * self.DPI) + int(0.4 * self.DPI) - int(0.2 * self.DPI)
        f_r, f_b = self.front_right - frame_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.2 * self.DPI) + int(0.2 * self.DPI) - int(0.1 * self.DPI) - int(0.05 * self.DPI), self.bleed_px + self.trim_h_px - frame_margin + int(0.5 * self.DPI) + int(0.2 * self.DPI) - int(0.3 * self.DPI) + int(0.4 * self.DPI) - int(0.2 * self.DPI)
        draw.rectangle([f_l, f_t, f_r, f_b], outline=self.colors['GOLD'], width=2)
        draw.rectangle([f_l + 5, f_t + 5, f_r - 5, f_b - 5], outline=self.colors['GOLD'], width=1)

        font_title = self._load_font('TITLE', 150)
        font_author = self._load_font('BOLD', self.author_font_size)
        
        title_text = "THE STOIC\nCITIZEN"
        lines = title_text.split('\n')
        curr_y = self.bleed_px + int(2.0 * self.DPI) + int(0.25 * self.DPI) + int(0.25 * self.DPI) + int(0.25 * self.DPI) - int(0.2 * self.DPI) - int(0.1 * self.DPI)
        for line in lines:
            tb = draw.textbbox((0, 0), line, font=font_title)
            tw, th = tb[2]-tb[0], tb[3]-tb[1]
            tx = self.front_left + (self.trim_w_px - tw) // 2 + int(0.5 * self.DPI) + int(0.25 * self.DPI) + int(0.25 * self.DPI) - int(0.1 * self.DPI) - int(0.1 * self.DPI) - int(0.2 * self.DPI)
            draw.text((tx, curr_y), line, font=font_title, fill=self.colors['TEXT'])
            curr_y += th + int(0.2 * self.DPI)

        author = "PHILIP HUFFMAN"
        ab = draw.textbbox((0, 0), author, font=font_author)
        aw = ab[2]-ab[0]
        ax = self.front_left + (self.trim_w_px - aw) // 2 + int(0.5 * self.DPI) + int(0.25 * self.DPI) + int(0.25 * self.DPI) - int(0.1 * self.DPI) - int(0.1 * self.DPI) - int(0.2 * self.DPI)
        ay = self.bleed_px + self.trim_h_px - int(self.author_bottom_margin * self.DPI) - ab[3] + int(0.25 * self.DPI) + int(0.25 * self.DPI) + int(0.25 * self.DPI)
        draw.text((ax, ay), author, font=font_author, fill=self.colors['TEXT_DIM'])

        font_spine = self._load_font('BOLD', 44)
        font_spine_small = self._load_font('REGULAR', 30)
        spine_title = "THE STOIC CITIZEN"
        stb = draw.textbbox((0, 0), spine_title, font=font_spine)
        stw, sth = stb[2]-stb[0], stb[3]-stb[1]
        st_img = Image.new("RGBA", (stw + 10, sth + 10), (0, 0, 0, 0))
        ImageDraw.Draw(st_img).text((5, 5), spine_title, font=font_spine, fill=self.colors['TEXT'])
        st_img = st_img.rotate(270, expand=True)
        img.paste(st_img, (self.spine_left + (self.spine_px - st_img.width)//2 + int(0.125 * self.DPI) + int(0.125 * self.DPI) + int(0.125 * self.DPI) - int(0.08 * self.DPI), self.bleed_px + int(1.0 * self.DPI)), st_img)

        spine_auth = "PHILIP HUFFMAN"
        sab = draw.textbbox((0, 0), spine_auth, font=font_spine_small)
        saw, sah = sab[2]-sab[0], sab[3]-sab[1]
        sa_img = Image.new("RGBA", (saw + 10, sah + 10), (0, 0, 0, 0))
        ImageDraw.Draw(sa_img).text((5, 5), spine_auth, font=font_spine_small, fill=self.colors['GOLD'])
        sa_img = sa_img.rotate(270, expand=True)
        img.paste(sa_img, (self.spine_left + (self.spine_px - sa_img.width)//2 + int(0.125 * self.DPI) + int(0.125 * self.DPI) + int(0.125 * self.DPI) - int(0.08 * self.DPI), self.bleed_px + self.trim_h_px - sa_img.height - int(0.6 * self.DPI)), sa_img)

        font_size_back = 32
        color_text_back = self.colors['TEXT']
        line_spacing_back = int(0.35 * self.DPI)
        font_back = self._load_font('REGULAR', font_size_back)
        font_quote = self._load_font('BOLD', 24)

        max_blurb_w = self.trim_w_px - self.safe_margin * 2 - int(0.5 * self.DPI) 
        blurb_text = ("The Stoic Citizen is a modern manual for the ancient art of civic virtue. It explores how the timeless principles of Stoicism can be applied to the complexities of modern citizenship, leadership, and individual responsibility. It suggests that the cultivation of the internal character is the only prerequisite for effective participation in the external world, and that true freedom is found not in the absence of constraint, but in the mastery of the self.\n\nBy bridging the gap between the Agora of Athens and the digital forums of today, this work provides a framework for maintaining internal tranquility while actively engaged in the pursuit of the common good. It provides a rigorous path toward a life of purpose, duty, and unwavering integrity, regardless of the prevailing winds of cultural volatility.")
        
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

        blurb_x, blurb_y = self.back_left + self.safe_margin + int(0.25 * self.DPI), self.bleed_px + int(1.1 * self.DPI)
        for i, line in enumerate(blurb_lines):
            draw.text((blurb_x, blurb_y + i * line_spacing_back), line, font=font_back, fill=color_text_back)
        
        blurb_bottom = blurb_y + len(blurb_lines) * line_spacing_back
        quote = '"He who is brave is free." — Seneca'
        qy = blurb_bottom + int(0.6 * self.DPI) - int(0.8 * self.DPI) 
        draw.text((blurb_x, qy), quote, font=font_quote, fill=self.colors['GOLD']) # x inherited from blurb_x

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
            px = self.back_left + self.safe_margin + int(0.25 * self.DPI)
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

        bio_x = blurb_x # Removing the additional .25\" offset to subtract .25\" relative to the current state
        bio_y = self.bleed_px + (self.trim_h_px // 2) + int(1.0 * self.DPI)
        for i, line in enumerate(bio_lines):
            draw.text((bio_x, bio_y + i * line_spacing_back), line, font=font_back, fill=color_text_back)

        barcode_w, barcode_h = int(2.0 * self.DPI), int(1.2 * self.DPI)
        barcode_x, barcode_y = self.back_right - self.safe_margin - barcode_w - int(0.125 * self.DPI) + int(0.0625 * self.DPI) - int(0.0625 * self.DPI), self.bleed_px + self.trim_h_px - self.safe_margin - barcode_h + int(0.5 * self.DPI) + int(0.125 * self.DPI) - int(0.0625 * self.DPI)
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
    print("The Stoic Citizen HC Cover generated successfully.")
