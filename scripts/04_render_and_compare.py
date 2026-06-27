#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_render_and_compare.py — Compare original vs repaired PDF page-by-page.

Renders both at the same DPI, computes a per-page pixel difference ratio, and flags pages
that changed. Use after the corrected PDF is placed via script 03. Produces a side-by-side
diff image per changed page in output/comparison_pdf/.

Usage:
    python scripts/04_render_and_compare.py --dpi 150
"""
import argparse
import json
import os

import fitz
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def find_one(folder, suffix=".pdf"):
    for f in os.listdir(folder):
        if f.lower().endswith(suffix):
            return os.path.join(folder, f)
    return None


def render(doc, i, dpi):
    pix = doc[i].get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    orig = find_one(os.path.join(ROOT, "input", "original_pdf"))
    rep = find_one(os.path.join(ROOT, "output", "repaired_pdf"))
    if not rep:
        raise SystemExit("No repaired PDF yet. Run script 03 first.")

    out = os.path.join(ROOT, "output", "comparison_pdf")
    os.makedirs(out, exist_ok=True)
    do, dr = fitz.open(orig), fitz.open(rep)
    n = min(do.page_count, dr.page_count)
    report = []
    for i in range(n):
        a, b = render(do, i, args.dpi), render(dr, i, args.dpi)
        if a.size != b.size:
            b = b.resize(a.size)
        diff = ImageChops.difference(a, b)
        bbox = diff.getbbox()
        ratio = 0.0 if not bbox else sum(diff.convert("L").getdata()) / (a.size[0] * a.size[1] * 255)
        changed = ratio > 0.0005
        if changed:
            combo = Image.new("RGB", (a.width * 2 + 20, a.height), "white")
            combo.paste(a, (0, 0)); combo.paste(b, (a.width + 20, 0))
            combo.save(os.path.join(out, f"compare_page_{i+1:02d}.png"))
        report.append({"page": i + 1, "diff_ratio": round(ratio, 6), "changed": changed})
        print(f"page {i+1:02d} diff={ratio:.6f} {'CHANGED' if changed else ''}")

    json.dump(report, open(os.path.join(ROOT, "data", "verification_results", "compare.json"),
                           "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\nComparison written. Review changed pages match expected Issue IDs only.")


if __name__ == "__main__":
    main()
