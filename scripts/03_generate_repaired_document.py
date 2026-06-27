#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_generate_repaired_document.py — Intake for the corrected PDF.

Strategy (user-confirmed): corrections are made in CANVA (the source design), NOT
rebuilt by code, to preserve the infographic layout 100%. This script therefore does
NOT synthesize a new layout. It registers the re-exported PDF as the "repaired" candidate
so the comparison/QA stage (04, 05) can run against it.

Usage:
    python scripts/03_generate_repaired_document.py path/to/Repaired_from_Canva.pdf
"""
import hashlib
import json
import os
import shutil
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEST = os.path.join(ROOT, "output", "repaired_pdf")


def main():
    if len(sys.argv) < 2:
        sys.exit("Provide the path to the Canva-re-exported PDF.\n"
                 "Until then, fix TH-001 in Canva per docs/CANVA_FIX_GUIDE.md and re-export.")
    src = sys.argv[1]
    os.makedirs(DEST, exist_ok=True)
    dst = os.path.join(DEST, "B2G_Repaired_candidate.pdf")
    shutil.copy2(src, dst)

    h = hashlib.sha256(open(dst, "rb").read()).hexdigest()
    doc = fitz.open(dst)
    info = {"file": os.path.basename(dst), "sha256": h, "page_count": doc.page_count}
    json.dump(info, open(os.path.join(DEST, "repaired_lock.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(info, ensure_ascii=False, indent=2))

    base = json.load(open(os.path.join(ROOT, "data", "baseline_lock.json"), encoding="utf-8"))
    if doc.page_count != base["page_count"]:
        print(f"!! WARNING: page count changed {base['page_count']} -> {doc.page_count} "
              f"(QA rule: หน้าต้องไม่หาย/ไม่เพี้ยน)")
    else:
        print("OK: page count matches baseline.")


if __name__ == "__main__":
    main()
