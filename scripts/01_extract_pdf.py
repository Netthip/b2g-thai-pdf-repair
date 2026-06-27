#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_extract_pdf.py — Render every PDF page to PNG and dump the raw text layer.

The source is a Canva-exported infographic whose embedded fonts carry no usable
ToUnicode map, so the extracted text layer is mojibake. We still dump it (for the
record / reproducibility) but the authoritative audit is performed on the
rendered page images.

Usage:
    python scripts/01_extract_pdf.py --dpi 150
"""
import argparse
import json
import os
import sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_DIR = os.path.join(ROOT, "input", "original_pdf")
IMG_DIR = os.path.join(ROOT, "data", "page_images")
TXT_DIR = os.path.join(ROOT, "data", "extracted_text")


def find_source_pdf():
    pdfs = [f for f in os.listdir(SRC_DIR) if f.lower().endswith(".pdf")]
    if not pdfs:
        sys.exit(f"No PDF found in {SRC_DIR}")
    return os.path.join(SRC_DIR, pdfs[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(TXT_DIR, exist_ok=True)

    src = find_source_pdf()
    doc = fitz.open(src)
    manifest = {"source": os.path.basename(src), "dpi": args.dpi, "pages": []}

    for i in range(doc.page_count):
        page = doc[i]
        pix = page.get_pixmap(dpi=args.dpi)
        img_name = f"page_{i+1:02d}.png"
        pix.save(os.path.join(IMG_DIR, img_name))

        raw = page.get_text("text")
        with open(os.path.join(TXT_DIR, f"page_{i+1:02d}.txt"), "w", encoding="utf-8") as f:
            f.write(raw)

        manifest["pages"].append({
            "page": i + 1,
            "image": img_name,
            "width_px": pix.width,
            "height_px": pix.height,
            "raw_text_len": len(raw),
            "image_count": len(page.get_images()),
        })
        print(f"page {i+1:02d}/{doc.page_count} rendered ({pix.width}x{pix.height})")

    with open(os.path.join(ROOT, "data", "render_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\nDone. {doc.page_count} pages -> {IMG_DIR}")


if __name__ == "__main__":
    main()
