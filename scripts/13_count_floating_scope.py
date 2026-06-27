#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
13_count_floating_scope.py — Quantify the DISPLAY-001 floating-mark scope as numbers
with per-page references.

Method: floating on weak mobile/web viewers affects Thai words that carry an upper/lower
vowel or tone mark (สระบน/ล่าง/วรรณยุกต์). We count:
  - text lines per page (from the PDF text layer — exact, mojibake-independent)
  - Thai words per page and words-with-combining-mark (from OCR + pythainlp, estimate)

Outputs: data/verification_results/floating_scope.csv / .md
"""
import csv
import os
import re
import fitz
from pythainlp.tokenize import word_tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "input", "original_pdf", "เล่ม พรบ ประชาชน.pdf")
OCR = os.path.join(ROOT, "data", "ocr")
MARK = re.compile(r"[ัิ-ฺ็-๎]")  # Thai upper/lower marks + tones
THAI = re.compile(r"[฀-๿]")


def main():
    doc = fitz.open(SRC)
    rows = []
    tot_lines = tot_words = tot_mark = 0
    for i in range(doc.page_count):
        d = doc[i].get_text("dict")
        lines = sum(1 for b in d["blocks"] for l in b.get("lines", [])
                    if any(s["text"].strip() for s in l["spans"]))
        words = mark = 0
        p = os.path.join(OCR, f"page_{i+1:02d}.txt")
        if os.path.exists(p):
            txt = open(p, encoding="utf-8").read()
            for t in word_tokenize(txt.replace("\n", " "), engine="newmm"):
                t = t.strip()
                if THAI.search(t):
                    words += 1
                    if MARK.search(t):
                        mark += 1
        rows.append({"หน้า PDF": i + 1, "หน้าพิมพ์": (i + 1 - 6) if i + 1 > 6 else "-",
                     "บรรทัดข้อความ": lines, "คำไทย(ประมาณ)": words,
                     "คำที่มีสระ/วรรณยุกต์ (เสี่ยงลอย)": mark})
        tot_lines += lines; tot_words += words; tot_mark += mark

    base = os.path.join(ROOT, "data", "verification_results")
    cols = ["หน้า PDF", "หน้าพิมพ์", "บรรทัดข้อความ", "คำไทย(ประมาณ)", "คำที่มีสระ/วรรณยุกต์ (เสี่ยงลอย)"]
    with open(os.path.join(base, "floating_scope.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    with open(os.path.join(base, "floating_scope.md"), "w", encoding="utf-8") as f:
        f.write("# ขอบเขตปัญหาสระลอย (DISPLAY-001) เป็นตัวเลข\n\n")
        f.write(f"- บรรทัดข้อความทั้งเล่ม: **{tot_lines:,}** บรรทัด\n")
        f.write(f"- คำไทยทั้งเล่ม (ประมาณจาก OCR): **{tot_words:,}** คำ\n")
        f.write(f"- คำที่มีสระบน/ล่าง หรือวรรณยุกต์ (เสี่ยงลอยบนมือถือ): **{tot_mark:,}** คำ"
                f" ({tot_mark*100//max(1,tot_words)}% ของคำไทย)\n\n")
        f.write("| หน้า | พิมพ์ | บรรทัด | คำไทย | คำเสี่ยงลอย |\n|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['หน้า PDF']} | {r['หน้าพิมพ์']} | {r['บรรทัดข้อความ']} | "
                    f"{r['คำไทย(ประมาณ)']} | {r['คำที่มีสระ/วรรณยุกต์ (เสี่ยงลอย)']} |\n")
    print(f"lines={tot_lines} words={tot_words} mark_words={tot_mark} "
          f"({tot_mark*100//max(1,tot_words)}%)")


if __name__ == "__main__":
    main()
