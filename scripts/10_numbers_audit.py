#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10_numbers_audit.py — Audit every monetary number and propose corrected formatting.

Rule (per reviewer): do NOT change the source values. For figures in ล้านบาท, reformat to
the standard #,##0.0000 (4 decimal places + thousands separators). Leave counts (คน/แห่ง/ราย/
ไร่/กม.), percentages, per-person baht, years, etc. unchanged.

Values are read from the PDF text layer (digits are reliable even though Thai is mojibake);
the unit/context for each number is matched from the OCR text (data/ocr, readable Thai).

Outputs:
  data/issue_registry/numbers_audit.csv / .xlsx / .md
"""
import csv
import os
import re

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "input", "original_pdf", "เล่ม พรบ ประชาชน.pdf")
OCR = os.path.join(ROOT, "data", "ocr")

NUM = re.compile(r'\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+')


COUNT_UNITS = ["คน", "ราย", "แห่ง", "ไร่", "กม", "กิโล", "ตัว", "ครัวเรือน", "โครงการ",
               "หน่วยงาน", "ชุมชน", "เครื่อง", "คัน", "บริษัท", "จุด", "ชุด", "หลัง",
               "เล่ม", "ฉบับ", "อัตรา", "ครั้ง", "ผืน", "สาขา"]


def classify(after, page_is_lb):
    """after = readable OCR text immediately following the number; page_is_lb = page is a
    ล้านบาท/budget context. Detect from the trailing unit first, then page default."""
    a = after.replace(" ", "")
    if a[:1] == "%" or after.lstrip()[:1] == "%":
        return "ร้อยละ/สัดส่วน", False
    if a.startswith("ล้านบาท") or a.startswith("ลบ") or a.startswith("ล้าน"):
        return "ล้านบาท", True
    if a.startswith("บาท"):
        return "บาท (ต่อหน่วย)", False
    for u in COUNT_UNITS:
        if a.startswith(u):
            return "จำนวน (นับ)", False
    # no trailing unit (e.g. table cell) -> use page default
    if page_is_lb:
        return "ล้านบาท", True
    return "ไม่ทราบหน่วย", False


def to4(numstr):
    v = float(numstr.replace(",", ""))
    return f"{v:,.4f}"


def main():
    doc = fitz.open(SRC)
    rows = []
    for i in range(doc.page_count):
        text = doc[i].get_text()
        ocr = ""
        p = os.path.join(OCR, f"page_{i+1:02d}.txt")
        if os.path.exists(p):
            ocr = open(p, encoding="utf-8").read()
        page_is_lb = ("ล้านบาท" in ocr) or ("ลบ." in ocr)
        for m in NUM.finditer(text):
            n = m.group()
            if "," not in n and "." not in n:
                continue
            dec = len(n.split(".")[1]) if "." in n else 0
            # find context in OCR (text after the number = its unit, usually)
            ctx = ""; after = ""
            src = ocr; idx = ocr.find(n)
            if idx < 0:
                src = ocr.replace(" ", ""); idx = src.find(n)
            if idx >= 0:
                ctx = src[max(0, idx - 8):idx + len(n) + 18].replace("\n", " ")
                after = src[idx + len(n):idx + len(n) + 12].replace("\n", " ")
            unit, is_lb = classify(after, page_is_lb)
            suggested = to4(n) if is_lb else n
            changed = "ใช่" if (is_lb and suggested != n) else ""
            rows.append({
                "หน้า PDF": i + 1, "หน้าพิมพ์": (i + 1 - 6) if i + 1 > 6 else "-",
                "ตัวเลขเดิม": n, "ทศนิยมเดิม": dec, "หน่วย(ตรวจ)": unit,
                "รูปแบบที่ควรเป็น": suggested, "ต้องแก้": changed,
                "บริบท(OCR)": ctx.strip(),
            })
    cols = ["หน้า PDF", "หน้าพิมพ์", "ตัวเลขเดิม", "ทศนิยมเดิม", "หน่วย(ตรวจ)",
            "รูปแบบที่ควรเป็น", "ต้องแก้", "บริบท(OCR)"]

    base = os.path.join(ROOT, "data", "issue_registry")
    with open(os.path.join(base, "numbers_audit.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

    # xlsx
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook(); ws = wb.active; ws.title = "Numbers"
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1F3864")
    for r in rows:
        ws.append([r[c] for c in cols])
        if r["ต้องแก้"] == "ใช่":
            for c in ws[ws.max_row]:
                c.fill = PatternFill("solid", fgColor="FFF2CC")
    widths = [9, 9, 16, 10, 16, 18, 8, 50]
    for i, wdt in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + i)].width = wdt
    ws.freeze_panes = "A2"
    wb.save(os.path.join(ROOT, "output", "audit_reports", "B2G_Numbers_Audit.xlsx"))

    # summary
    lb = [r for r in rows if r["หน่วย(ตรวจ)"] == "ล้านบาท"]
    need = [r for r in rows if r["ต้องแก้"] == "ใช่"]
    from collections import Counter
    bytype = Counter(r["หน่วย(ตรวจ)"] for r in rows)
    md = ["# ตารางตรวจตัวเลขทั้งเล่ม\n", f"- ตัวเลขทั้งหมด: **{len(rows)}**",
          f"- เป็นล้านบาท: **{len(lb)}**  | ต้องจัดรูปแบบ 4 ทศนิยม: **{len(need)}**",
          "- แยกตามหน่วย: " + ", ".join(f"{k}={v}" for k, v in bytype.most_common()), "",
          "| หน้า | ตัวเลขเดิม | ทศ. | หน่วย | ควรเป็น | แก้ | บริบท |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['หน้า PDF']} | {r['ตัวเลขเดิม']} | {r['ทศนิยมเดิม']} | {r['หน่วย(ตรวจ)']} | "
                  f"{r['รูปแบบที่ควรเป็น']} | {r['ต้องแก้']} | {r['บริบท(OCR)'][:40]} |")
    open(os.path.join(base, "numbers_audit.md"), "w", encoding="utf-8").write("\n".join(md))

    print(f"total={len(rows)} | ล้านบาท={len(lb)} | ต้องแก้รูปแบบ={len(need)}")
    print("by unit:", dict(bytype))


if __name__ == "__main__":
    main()
