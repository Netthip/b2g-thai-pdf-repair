#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
14_add_branding.py — Append a polite colophon (credit) page to make the BRANDED edition.
Kept separate from the clean edition so the official-use file stays unbranded.

Output: output/final_delivery/B2G_Repaired_Final_Branded.pdf
"""
import io
import os
import fitz
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(ROOT, "output", "final_delivery", "B2G_Repaired_Final.pdf")
OUT = os.path.join(ROOT, "output", "final_delivery", "B2G_Repaired_Final_Branded.pdf")
TH = r"C:\Windows\Fonts\tahoma.ttf"
THB = r"C:\Windows\Fonts\tahomabd.ttf"
NAVY = (0.10, 0.18, 0.34); GRAY = (0.42, 0.42, 0.42); MID = (0.20, 0.30, 0.5)


def colophon_image(w, h):
    doc = fitz.open(); pg = doc.new_page(width=w, height=h)
    pg.insert_font(fontname="th", fontfile=TH); pg.insert_font(fontname="thb", fontfile=THB)
    pg.draw_rect(fitz.Rect(0, 0, w, h), color=None, fill=(0.97, 0.98, 1.0))
    # top + bottom navy bars
    pg.draw_rect(fitz.Rect(0, 0, w, 10), color=None, fill=NAVY)
    pg.draw_rect(fitz.Rect(0, h - 36, w, h), color=None, fill=NAVY)
    cx = w / 2

    def ctext(y, s, size, font="th", color=(0, 0, 0), ff=TH):
        pg.insert_textbox(fitz.Rect(0, y, w, y + size * 2.0), s, fontname=font, fontfile=ff,
                          fontsize=size, color=color, align=1)

    ctext(138, "งบประมาณฉบับประชาชน ประจำปีงบประมาณ พ.ศ. 2570", 12, "th", GRAY)
    ctext(168, "ฉบับตรวจแก้ภาษาไทย", 12, "th", GRAY)
    ctext(255, "B2G", 92, "thb", NAVY, THB)
    ctext(372, "Bo + Giho", 18, "th", MID)
    pg.draw_line((cx - 130, 415), (cx + 130, 415), color=NAVY, width=1)
    ctext(445, "ตรวจแก้และทบทวนภาษาไทยโดย", 15, "th", (0.1, 0.1, 0.1))
    ctext(478, "นางสาวเนตรทิพย์ GiftzaXBOHO", 22, "thb", NAVY, THB)
    ctext(556, "B2G เป็นชื่อกระบวนการตรวจแก้เอกสารภาษาไทย", 10.5, "th", GRAY)
    ctext(574, "มิใช่ชื่อหน่วยงานทางการ", 10.5, "th", GRAY)
    ctext(715, "จัดทำด้วยกระบวนการตรวจสอบย้อนกลับได้ · มิถุนายน 2569", 10, "th", GRAY)
    ctext(h - 26, "B2G  ·  Bo + Giho", 9, "thb", (1, 1, 1), THB)

    pix = pg.get_pixmap(dpi=180)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def main():
    book = fitz.open(BASE)
    w, h = book[0].rect.width, book[0].rect.height
    img = colophon_image(w, h)
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=90)
    pg = book.new_page(width=w, height=h)
    pg.insert_image(pg.rect, stream=buf.getvalue())
    book.save(OUT, deflate=True, garbage=4)
    print(f"Branded edition: {OUT} ({book.page_count} pages, {os.path.getsize(OUT)//1024//1024} MB)")


if __name__ == "__main__":
    main()
