#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Round 2 — render high-zoom crops of EVERY heading / colored title bar and pack them into
labeled contact sheets for human/AI zoom verification.

Heading = any text span with font size >= THRESHOLD pt (captures section dividers, page
titles, colored title bars, big number callouts; excludes ~10-12pt body text).
Each crop is labeled "pNN" (PDF page). Strips flow into sheets ~1800px tall.
"""
import os
import fitz
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "input", "original_pdf", "เล่ม พรบ ประชาชน.pdf")
OUT = os.path.join(ROOT, "data", "round2")
LABELFONT = r"C:\Windows\Fonts\tahomabd.ttf"

THRESHOLD = 18.0   # pt
ZOOM = 2.3
MAX_W = 1500       # crop width cap (px)
SHEET_H = 1920     # max sheet height (px)
PAD = 10


def heading_lines(page):
    """Return list of (bbox, max_size) for lines containing a span >= THRESHOLD."""
    d = page.get_text("dict")
    out = []
    for b in d["blocks"]:
        for l in b.get("lines", []):
            sizes = [s["size"] for s in l["spans"] if s["text"].strip()]
            if sizes and max(sizes) >= THRESHOLD:
                x0 = min(s["bbox"][0] for s in l["spans"])
                y0 = min(s["bbox"][1] for s in l["spans"])
                x1 = max(s["bbox"][2] for s in l["spans"])
                y1 = max(s["bbox"][3] for s in l["spans"])
                out.append((fitz.Rect(x0 - 3, y0 - 4, x1 + 3, y1 + 6), max(sizes)))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    doc = fitz.open(SRC)
    try:
        lf = ImageFont.truetype(LABELFONT, 22)
    except Exception:
        lf = ImageFont.load_default()

    strips = []  # (label, PIL image)
    total = 0
    for i in range(doc.page_count):
        page = doc[i]
        lines = heading_lines(page)
        # sort top-to-bottom
        lines.sort(key=lambda r: r[0].y0)
        for rect, size in lines:
            if rect.width < 8 or rect.height < 6:
                continue
            pix = page.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=rect)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            if img.width > MAX_W:
                img = img.resize((MAX_W, int(img.height * MAX_W / img.width)))
            strips.append((f"p{i+1:02d} ({size:.0f}pt)", img))
            total += 1

    # pack strips into sheets
    sheets = []
    cur, h = [], 0
    for label, img in strips:
        strip_h = img.height + 26 + PAD
        if h + strip_h > SHEET_H and cur:
            sheets.append(cur); cur, h = [], 0
        cur.append((label, img)); h += strip_h
    if cur:
        sheets.append(cur)

    for si, sheet in enumerate(sheets):
        w = max(img.width for _, img in sheet) + 2 * PAD
        h = sum(img.height + 26 + PAD for _, img in sheet) + PAD
        canvas = Image.new("RGB", (w, h), "white")
        draw = ImageDraw.Draw(canvas)
        y = PAD
        for label, img in sheet:
            draw.text((PAD, y), label, fill=(180, 30, 30), font=lf)
            y += 22
            canvas.paste(img, (PAD, y))
            draw.line((0, y - 2, w, y - 2), fill=(220, 220, 220))
            y += img.height + PAD
        canvas.save(os.path.join(OUT, f"sheet_{si+1:02d}.png"))

    print(f"heading lines: {total}  ->  sheets: {len(sheets)}  in {OUT}")


if __name__ == "__main__":
    main()
