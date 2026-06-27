#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the executive audit report as a Thai PDF (Tahoma) with evidence images."""
import os
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT = r"C:\Windows\Fonts\tahoma.ttf"
FONTB = r"C:\Windows\Fonts\tahomabd.ttf"
EV = os.path.join(ROOT, "output", "audit_reports", "evidence")
OUT = os.path.join(ROOT, "output", "audit_reports", "B2G_Original_Audit_Report.pdf")

NAVY = (0.12, 0.22, 0.39)
RED = (0.66, 0.24, 0.16)
GRAY = (0.3, 0.3, 0.3)


def main():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_font(fontname="th", fontfile=FONT)
    page.insert_font(fontname="thb", fontfile=FONTB if os.path.exists(FONTB) else FONT)
    M = 50
    y = [70]

    def line(txt, size=11, font="th", color=(0, 0, 0), dy=None, x=M):
        page.insert_text((x, y[0]), txt, fontname=font, fontsize=size, color=color)
        y[0] += dy if dy else size + 6

    def rule():
        page.draw_line((M, y[0]), (545, y[0]), color=NAVY, width=0.8); y[0] += 12

    line("B2G — รายงานสรุปผลตรวจ PDF ต้นฉบับ (Audit รอบที่ 1)", 16, "thb", NAVY, 24)
    line("เอกสาร: งบประมาณฉบับประชาชน ประจำปีงบประมาณ พ.ศ. 2570 (72 หน้า, Canva)", 10, "th", GRAY)
    line("วันที่ตรวจ: 2026-06-27   ผู้ตรวจ: B2G pipeline (visual-assisted)", 10, "th", GRAY)
    line("SHA-256: d304742f0d8e0971fa93affcf2beb43e6fef5e7d848f6db6e322e57aafb1b9c6", 8.5, "th", GRAY)
    rule()

    line("1. ตัวเลขสรุป", 13, "thb", NAVY, 20)
    for t in [
        "• จำนวนหน้าทั้งหมด: 72   (หน้าว่าง 2 หน้า: หน้า 2, 4)",
        "• ตรวจเต็มหน้า (150 DPI): 72/72 หน้า",
        "• ข้อผิดพลาดที่ยืนยันแล้ว: 1 รายการ  (หน้า PDF 66 / หน้าพิมพ์ 60)",
        "• ต้องตรวจทานโดยมนุษย์ (Human Review): 2 รายการ",
    ]:
        line(t, 11)
    y[0] += 6

    line("2. ข้อผิดพลาดที่ยืนยันแล้ว — TH-001 (ความรุนแรง: สูง)", 13, "thb", RED, 20)
    for t in [
        "ตำแหน่ง: หน้า PDF 66 (หน้าพิมพ์ 60) — หัวเรื่องหมวดหลัก บรรทัดที่ 2",
        "ข้อความที่พบ:   การปฏฐูปกฎหมาย   (สระ ิ หาย และ ร เพี้ยนเป็น ฐ)",
        "ข้อความที่ควรเป็น:   การปฏิรูปกฎหมาย",
        "ยืนยันจาก: สารบัญ (หน้า 5), หน้า 22, หน้า 68 + ฟอนต์รายสแปนตรงกันแต่กลิฟต่าง",
    ]:
        line(t, 11)
    y[0] += 4

    # evidence images side by side
    try:
        w = 230
        page.insert_textbox(fitz.Rect(M, y[0], M + w, y[0] + 14), "จุดที่ผิด (หน้า 66)",
                            fontname="th", fontsize=9, color=RED)
        page.insert_textbox(fitz.Rect(M + w + 20, y[0], M + 2 * w, y[0] + 14),
                            "อ้างอิงที่ถูก (หน้า 68)", fontname="th", fontsize=9, color=NAVY)
        y[0] += 14
        r1 = fitz.Rect(M, y[0], M + w, y[0] + 95)
        r2 = fitz.Rect(M + w + 20, y[0], M + 2 * w + 20, y[0] + 95)
        page.insert_image(r1, filename=os.path.join(EV, "TH-001_page66_found_wrong.png"))
        page.insert_image(r2, filename=os.path.join(EV, "TH-001_page68_correct_reference.png"))
        y[0] += 105
    except Exception as e:
        line(f"[evidence image error: {e}]", 9, "th", RED)

    rule()
    line("3. ความตรงไปตรงมา (ตามหลัก QA)", 13, "thb", NAVY, 20)
    box = fitz.Rect(M, y[0], 545, y[0] + 90)
    page.insert_textbox(
        box,
        "• ตรวจครบ 3 รอบ: เต็มหน้า 72/72 · ซูมหัวข้อ 365 บรรทัด · OCR body ทั้งเล่ม\n"
        "• รอบ 2 (หัวข้อ) พบเพี้ยน 1 = TH-001; รอบ 3 (body OCR+พจนานุกรม) = 0 errors\n"
        "• ข้อผิดพลาดยืนยันแล้วทั้งเล่ม = 1 จุดเดียว (TH-001 หัวเรื่องหน้า 66); Human Review ปิดครบ\n"
        "• เมื่อแก้ TH-001 ใน Canva + export ใหม่ + รัน 03–04 ยืนยัน → เล่มผ่าน Quality Gate",
        fontname="th", fontsize=10.5, color=(0, 0, 0))
    y[0] = box.y1 + 16
    rule()
    line("เอกสารแนบ: B2G_Original_Audit_Report.xlsx · B2G_Page_by_Page_Verification.xlsx", 9, "th", GRAY)
    line("B2G (Bo + Giho) · ตรวจแก้และทบทวนเนื้อหาโดย นางสาวเนตรทิพย์ GiftzaXBOHO", 9, "th", GRAY)

    doc.save(OUT)
    print("written:", OUT)


if __name__ == "__main__":
    main()
