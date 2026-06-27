#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
08_build_image_pdf.py — Build the repaired, viewer-robust PDF.

WHY: The source Canva PDF positions Thai combining marks in a way that pro renderers
(MuPDF/Adobe) show correctly but weak mobile/web viewers misplace (vowels/tone marks
"float" onto the wrong consonant) — the citizen audience sees broken text. Rasterizing
each page (rendered with correct positions) bakes the text to pixels, so it displays
IDENTICALLY and correctly on EVERY viewer. The mojibake text layer is dropped (it was
unusable anyway).

Also bakes the TH-001 correction on page 66: headline 'การปฏฐูป...' -> 'การปฏิรูปกฎหมาย'.

Output: output/final_delivery/B2G_Repaired_Final.pdf
"""
import io
import os
import fitz
from PIL import Image, ImageDraw
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "input", "original_pdf", "เล่ม พรบ ประชาชน.pdf")
OUT = os.path.join(ROOT, "output", "final_delivery", "B2G_Repaired_Final.pdf")
THAI_BOLD = r"C:\Windows\Fonts\tahomabd.ttf"

DPI = 180
JPEG_Q = 88
NAVY = (0, 38, 68)


def patch_th001(page, im, sc):
    """Cover the corrupted page-66 headline line 2 and redraw correct Thai."""
    x0, y0, x1, y1 = 97.5, 219.0, 486.6, 302.1            # original line-2 span (pt)
    X0, Y0, X1, Y1 = [int(round(v * sc)) for v in (x0, y0, x1, y1)]
    bg = Counter(im.crop((X1 + 20, Y0 + 10, min(im.width, X1 + 200), Y1 - 10))
                 .getdata()).most_common(1)[0][0]
    ImageDraw.Draw(im).rectangle([X0 - 8, Y0 + 2, X1 + 12, Y1 - 2], fill=bg)
    tmp = fitz.open(); tp = tmp.new_page(width=1400, height=400)
    tp.insert_font(fontname="thb", fontfile=THAI_BOLD)
    tp.insert_text((20, 200), "การปฏิรูปกฎหมาย", fontname="thb", fontsize=170,
                   color=(NAVY[0] / 255, NAVY[1] / 255, NAVY[2] / 255))
    tpx = tp.get_pixmap(dpi=180, alpha=True)
    ti = Image.frombytes("RGBA", (tpx.width, tpx.height), tpx.samples)
    ti = ti.crop(ti.getbbox())
    target_w = X1 - X0
    ti = ti.resize((target_w, int(ti.height * target_w / ti.width)))
    im.paste(ti, (X0, Y0 + 4), ti)
    return im


def main():
    doc = fitz.open(SRC)
    sc = DPI / 72
    out = fitz.open()
    for i in range(doc.page_count):
        page = doc[i]
        pix = page.get_pixmap(dpi=DPI)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        if i == 65:  # page 66 -> TH-001 fix
            im = patch_th001(page, im, sc)
        buf = io.BytesIO(); im.save(buf, format="JPEG", quality=JPEG_Q)
        p = out.new_page(width=page.rect.width, height=page.rect.height)
        p.insert_image(p.rect, stream=buf.getvalue())
        print(f"page {i+1:02d}/{doc.page_count}")
    out.set_metadata({"title": "งบประมาณฉบับประชาชน ปีงบประมาณ พ.ศ. 2570 (ฉบับแก้ไข B2G)",
                      "author": "สำนักงบประมาณ", "producer": "B2G Thai PDF Repair"})
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.save(OUT, deflate=True, garbage=4)
    print("\nSaved:", OUT, f"({os.path.getsize(OUT)//1024//1024} MB, {out.page_count} pages)")


if __name__ == "__main__":
    main()
