#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07_body_ocr_proofread.py — OCR-assisted body-text proofread (closes HR-001).

The PDF text layer is mojibake, so we OCR each page image (Thai+Eng), tokenize with
pythainlp, and flag Thai tokens NOT found in the Thai dictionary. Flags are candidates
for either (a) genuine source corruption like TH-001, or (b) OCR noise / proper nouns —
which a human/zoom pass then adjudicates. Output is written UTF-8 (console can't show Thai).

Outputs:
  data/ocr/page_NN.txt              full OCR text per page
  data/verification_results/body_candidates.md   flagged tokens with page + context
"""
import argparse
import os
import re

import fitz
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.environ["TESSDATA_PREFIX"] = os.path.join(ROOT, "tessdata")
SRC = os.path.join(ROOT, "input", "original_pdf", "เล่ม พรบ ประชาชน.pdf")
OCR_DIR = os.path.join(ROOT, "data", "ocr")
THAI = re.compile(r"^[ก-๙]+$")

from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_words
WORDS = set(thai_words())
# common valid fragments / particles that newmm may split oddly
WHITELIST = set("ฯลฯ ณ ฤ ฯ".split())


def ocr_page(doc, i, dpi_zoom=3):
    pix = doc[i].get_pixmap(matrix=fitz.Matrix(dpi_zoom, dpi_zoom))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return pytesseract.image_to_string(img, lang="tha+eng")


def flag_tokens(text):
    flags = []
    toks = word_tokenize(text.replace("\n", " "), engine="newmm")
    for j, t in enumerate(toks):
        t = t.strip()
        if not t or not THAI.match(t):
            continue
        if len(t) < 3:  # short tokens too noisy
            continue
        if t in WORDS or t in WHITELIST:
            continue
        ctx = "".join(toks[max(0, j - 2):j + 3])
        flags.append((t, ctx))
    return flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="", help="comma list of PDF pages (1-based); empty=all")
    args = ap.parse_args()
    os.makedirs(OCR_DIR, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "data", "verification_results"), exist_ok=True)

    doc = fitz.open(SRC)
    if args.pages:
        pages = [int(x) - 1 for x in args.pages.split(",")]
    else:
        pages = range(doc.page_count)

    md = ["# Body OCR proofread — flagged candidates\n",
          "_Thai tokens not in dictionary (OCR-based). Each must be zoom-checked: "
          "genuine corruption vs OCR-noise/proper-noun._\n"]
    total_flags = 0
    for i in pages:
        text = ocr_page(doc, i)
        with open(os.path.join(OCR_DIR, f"page_{i+1:02d}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        flags = flag_tokens(text)
        total_flags += len(flags)
        if flags:
            md.append(f"\n## หน้า PDF {i+1} ({len(flags)} flag)\n")
            for t, ctx in flags:
                md.append(f"- `{t}`  …{ctx}…")
        print(f"page {i+1:02d}: {len(flags)} flags")

    md.append(f"\n\n**รวม flag: {total_flags}**")
    with open(os.path.join(ROOT, "data", "verification_results", "body_candidates.md"),
              "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("total flags:", total_flags)


if __name__ == "__main__":
    main()
