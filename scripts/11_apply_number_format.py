#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
11_apply_number_format.py — Final repaired PDF: reformat ล้านบาท numbers to 4 decimals
(#,##0.0000), baked as pixels. Values unchanged; only formatting.

Layout-safe: each replacement is FIT inside the original space so nothing overlaps —
  * number + adjacent 'ล้านบาท' unit  -> re-render the group, scaled to the group box
  * table cell (no adjacent unit)      -> right-align, scaled to the available cell width
Only the 120 numbers confidently classified ล้านบาท (numbers_audit.csv, ต้องแก้=ใช่) are
touched. Also bakes the TH-001 page-66 headline fix.

Output: output/final_delivery/B2G_Repaired_Final.pdf
"""
import csv
import io
import os
import re
from collections import Counter, defaultdict
import fitz
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "input", "original_pdf", "เล่ม พรบ ประชาชน.pdf")
OUT = os.path.join(ROOT, "output", "final_delivery", "B2G_Repaired_Final.pdf")
TAHOMA = r"C:\Windows\Fonts\tahoma.ttf"
THB = r"C:\Windows\Fonts\tahomabd.ttf"
DPI = 180; JPEG_Q = 88
ISNUM = re.compile(r'^\d[\d,\.]*$')


def load_targets():
    t = defaultdict(dict)
    with open(os.path.join(ROOT, "data", "issue_registry", "numbers_audit.csv"),
              encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["ต้องแก้"] == "ใช่":
                t[int(r["หน้า PDF"])][r["ตัวเลขเดิม"]] = r["รูปแบบที่ควรเป็น"]
    return t


def dist(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2


def colors(im, X0, Y0, X1, Y1):
    ring = im.crop((max(0, X0-3), Y0, min(im.width, X1+10), Y1))
    bg = Counter(ring.getdata()).most_common(1)[0][0]
    cell = list(im.crop((X0, Y0, X1, Y1)).getdata())
    text = max(cell, key=lambda p: dist(p, bg)) if cell else (0, 0, 0)
    return bg, text


def render_fit(s, color, max_w, max_h, fontfile):
    t = fitz.open(); p = t.new_page(width=2400, height=300)
    p.insert_font(fontname="f", fontfile=fontfile)
    p.insert_text((10, 210), s, fontname="f", fontsize=200,
                  color=(color[0]/255, color[1]/255, color[2]/255))
    px = p.get_pixmap(dpi=180, alpha=True)
    im = Image.frombytes("RGBA", (px.width, px.height), px.samples).crop(
        Image.frombytes("RGBA", (px.width, px.height), px.samples).getbbox())
    sc = min(max_w / im.width, max_h / im.height)
    return im.resize((max(1, int(im.width*sc)), max(1, int(im.height*sc))))


def patch_th001(page, im, sc):
    x0, y0, x1, y1 = 97.5, 219.0, 486.6, 302.1
    X0, Y0, X1, Y1 = [int(round(v*sc)) for v in (x0, y0, x1, y1)]
    bg = Counter(im.crop((X1+20, Y0+10, min(im.width, X1+200), Y1-10)).getdata()).most_common(1)[0][0]
    ImageDraw.Draw(im).rectangle([X0-8, Y0+2, X1+12, Y1-2], fill=bg)
    ti = render_fit("การปฏิรูปกฎหมาย", (0, 38, 68), X1-X0, int((Y1-Y0)*0.95), THB)
    im.paste(ti, (X0, Y0+4), ti)


def main():
    targets = load_targets()
    src = fitz.open(SRC); out = fitz.open(); sc = DPI/72
    n = 0
    for i in range(src.page_count):
        page = src[i]
        pix = page.get_pixmap(dpi=DPI)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        pt = targets.get(i+1, {})
        if pt:
            words = page.get_text("words")
            for w in words:
                if w[4] not in pt:
                    continue
                wx0, wy0, wx1, wy1 = w[0], w[1], w[2], w[3]
                h = wy1 - wy0
                same = [u for u in words if min(u[3], wy1) - max(u[1], wy0) > 0.4*h]
                rn = [u for u in same if u[0] >= wx1 - 1]
                ln = [u for u in same if u[2] <= wx0 + 1]
                rn.sort(key=lambda u: u[0]); ln.sort(key=lambda u: -u[2])
                X0, Y0, X1, Y1 = [int(round(v*sc)) for v in (wx0, wy0, wx1, wy1)]
                unit_beside = rn and (rn[0][0] - wx1) < h*2.0 and not ISNUM.match(rn[0][4].strip())
                if unit_beside:
                    g = (wx0, min(wy0, rn[0][1]), rn[0][2], max(wy1, rn[0][3]))
                    GX0, GY0, GX1, GY1 = [int(round(v*sc)) for v in g]
                    bg, tc = colors(im, X0, Y0, X1, Y1)
                    ImageDraw.Draw(im).rectangle([GX0-1, GY0-1, GX1+1, GY1+1], fill=bg)
                    ti = render_fit(pt[w[4]] + " ล้านบาท", tc, GX1-GX0, GY1-GY0, TAHOMA)
                    im.paste(ti, (GX0, GY0 + (GY1-GY0-ti.height)//2), ti)
                else:
                    leftb = (ln[0][2]*sc + h*0.4*sc) if ln else max(0, X0 - h*6*sc)
                    avail = X1 - int(leftb)
                    bg, tc = colors(im, X0, Y0, X1, Y1)
                    ImageDraw.Draw(im).rectangle([X0-1, Y0-1, X1+1, Y1+1], fill=bg)
                    ti = render_fit(pt[w[4]], tc, max(10, avail), Y1-Y0, TAHOMA)
                    im.paste(ti, (X1 - ti.width, Y0 + (Y1-Y0-ti.height)//2), ti)
                n += 1
        if i == 65:
            patch_th001(page, im, sc)
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=JPEG_Q)
        p = out.new_page(width=page.rect.width, height=page.rect.height)
        p.insert_image(p.rect, stream=buf.getvalue())
    out.set_metadata({"title": "งบประมาณฉบับประชาชน 2570 (ฉบับแก้ไข B2G)",
                      "author": "สำนักงบประมาณ", "producer": "B2G Thai PDF Repair"})
    out.save(OUT, deflate=True, garbage=4)
    print(f"reformatted {n} numbers | {out.page_count} pages | {os.path.getsize(OUT)//1024//1024} MB")


if __name__ == "__main__":
    main()
