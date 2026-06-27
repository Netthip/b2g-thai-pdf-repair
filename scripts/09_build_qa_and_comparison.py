#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build B2G_QA_Final_Report.pdf and B2G_Comparison.pdf (before/after page 66)."""
import io
import os
import fitz
from PIL import Image, ImageDraw
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "input", "original_pdf", "เล่ม พรบ ประชาชน.pdf")
TH = r"C:\Windows\Fonts\tahoma.ttf"
THB = r"C:\Windows\Fonts\tahomabd.ttf"
NAVY = (0.12, 0.22, 0.39); RED = (0.66, 0.24, 0.16); GRAY = (0.3, 0.3, 0.3)


def qa_pdf():
    doc = fitz.open(); pg = doc.new_page(width=595, height=842)
    pg.insert_font(fontname="th", fontfile=TH); pg.insert_font(fontname="thb", fontfile=THB)
    y = [60]
    def line(t, s=11, f="th", c=(0, 0, 0), dy=None, x=50):
        pg.insert_text((x, y[0]), t, fontname=f, fontsize=s, color=c); y[0] += dy or s + 6
    line("B2G — รายงาน QA ฉบับสุดท้าย", 16, "thb", NAVY, 24)
    line("เอกสาร: งบประมาณฉบับประชาชน ปีงบประมาณ พ.ศ. 2570 (72 หน้า)", 10, "th", GRAY)
    line("ไฟล์ซ่อมแล้ว: B2G_Repaired_Final.pdf (72 หน้า, ~35 MB, 180 DPI, image-based)", 10, "th", GRAY)
    pg.draw_line((50, y[0]), (545, y[0]), color=NAVY, width=0.8); y[0] += 14
    line("ข้อผิดพลาด ก่อนแก้ → หลังแก้", 13, "thb", NAVY, 20)
    box = fitz.Rect(50, y[0], 545, y[0] + 150)
    pg.insert_textbox(box,
        "DISPLAY-001 (ทั้งเล่ม): สระ/วรรณยุกต์ลอยทับตัวถัดไปบน viewer มือถือ/เว็บ\n"
        "   ก่อน: พบ (ผู้ใช้ยืนยันด้วยภาพหน้าจอจริง หน้า 7 'ปัญหา'→'ปั ญ')\n"
        "   หลัง: แก้แล้ว — แปลงทุกหน้าเป็นภาพ ไม่มี text layer ให้ลอย → ทุก viewer เห็นตรงกัน\n\n"
        "TH-001 (หน้า 66): หัวเรื่อง 'การปฏฐูปกฎหมาย' (สระ ิ หาย + ร→ฐ)\n"
        "   ก่อน: พบ    หลัง: แก้แล้ว — overlay 'การปฏิรูปกฎหมาย' เบคเป็นภาพ",
        fontname="th", fontsize=10.5); y[0] = box.y1 + 8
    line("หลักฐานหลังแก้ (B2G_Repaired_Final.pdf)", 13, "thb", NAVY, 20)
    for t in ["• จำนวนหน้า = 72 (เท่าเดิม ไม่หาย/ไม่สลับ)",
              "• live-text characters = 0 → ยืนยันไม่มี text layer ให้สระลอยได้",
              "• หน้า 66 หัวเรื่อง 'การปฏิรูปกฎหมาย' ถูกต้อง",
              "• เนื้อหา/ภาพ/ตาราง/ลำดับหน้า ตรงต้นฉบับ"]:
        line(t, 11)
    y[0] += 4
    line("การตรวจ 4 รอบ", 13, "thb", NAVY, 20)
    for t in ["1) เต็มหน้า 150 DPI 72/72  2) ซูมหัวข้อ 365 บรรทัด (พบ TH-001)",
              "3) OCR body ทั้งเล่ม (body 0 errors)  4) ผู้ใช้รายงาน+เทียบ render → DISPLAY-001"]:
        line(t, 10.5)
    y[0] += 6
    line("ข้อจำกัด / Human Review", 13, "thb", RED, 20)
    box2 = fitz.Rect(50, y[0], 545, y[0] + 70)
    pg.insert_textbox(box2,
        "• ฉบับภาพ: คัดลอก/ค้นหาข้อความไม่ได้ (ต้นฉบับ text ก็เสียอยู่แล้ว)\n"
        "• ต้องการฉบับ select ข้อความได้/accessibility → แก้ที่ Canva ต้นฉบับ (แชร์สิทธิ์ก่อน)\n"
        "• แนะนำทดสอบเปิดบนมือถือจริงเพื่อยืนยันสระไม่ลอย (การตรวจขั้นสุดท้ายโดยมนุษย์)",
        fontname="th", fontsize=10.5); y[0] = box2.y1 + 12
    line("ตรวจแก้และทบทวนเนื้อหาโดย นางสาวเนตรทิพย์ GiftzaXBOHO · B2G (Bo + Giho)", 9, "th", GRAY)
    out = os.path.join(ROOT, "output", "audit_reports", "B2G_QA_Final_Report.pdf")
    doc.save(out); print("QA pdf:", out)


def patch66(page, im, sc):
    x0, y0, x1, y1 = 97.5, 219.0, 486.6, 302.1
    X0, Y0, X1, Y1 = [int(round(v * sc)) for v in (x0, y0, x1, y1)]
    bg = Counter(im.crop((X1 + 20, Y0 + 10, min(im.width, X1 + 200), Y1 - 10)).getdata()).most_common(1)[0][0]
    ImageDraw.Draw(im).rectangle([X0 - 8, Y0 + 2, X1 + 12, Y1 - 2], fill=bg)
    tmp = fitz.open(); tp = tmp.new_page(width=1400, height=400)
    tp.insert_font(fontname="thb", fontfile=THB)
    tp.insert_text((20, 200), "การปฏิรูปกฎหมาย", fontname="thb", fontsize=170, color=(0, 38/255, 68/255))
    tpx = tp.get_pixmap(dpi=180, alpha=True); ti = Image.frombytes("RGBA", (tpx.width, tpx.height), tpx.samples)
    ti = ti.crop(ti.getbbox()); tw = X1 - X0; ti = ti.resize((tw, int(ti.height * tw / ti.width)))
    im.paste(ti, (X0, Y0 + 4), ti); return im


def comparison_pdf():
    doc = fitz.open(SRC); sc = 150 / 72
    before = doc[65].get_pixmap(dpi=150)
    imb = Image.frombytes("RGB", (before.width, before.height), before.samples)
    ima = patch66(doc[65], imb.copy(), sc)
    out = fitz.open(); W, H = 595, 842
    pg = out.new_page(width=W, height=H)
    pg.insert_font(fontname="thb", fontfile=THB)
    pg.insert_text((40, 50), "B2G — เปรียบเทียบก่อน/หลังแก้ (TH-001 หน้า 66)", fontname="thb", fontsize=15, color=NAVY)
    # crop headline band for clarity
    band = (0, int(120 * sc), imb.width, int(320 * sc))
    for label, img, x in [("ก่อนแก้ (พบ 'ปฏฐู')", imb.crop(band), 40), ("หลังแก้ ('ปฏิรูป')", ima.crop(band), 40)]:
        pass
    yb = 80
    for label, img in [("ก่อนแก้: 'การปฏฐูปกฎหมาย'", imb.crop(band)), ("หลังแก้: 'การปฏิรูปกฎหมาย'", ima.crop(band))]:
        pg.insert_text((40, yb), label, fontname="thb", fontsize=11, color=RED if "ก่อน" in label else NAVY)
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=88)
        r = fitz.Rect(40, yb + 8, 555, yb + 8 + (515 * img.height / img.width))
        pg.insert_image(r, stream=buf.getvalue()); yb = r.y1 + 24
    pg.insert_text((40, yb + 4), "หมายเหตุ: ปัญหา 'สระลอย' (DISPLAY-001) เห็นเฉพาะบน viewer มือถือ/เว็บ จึงเทียบด้วยภาพนิ่งไม่ได้",
                   fontname="thb", fontsize=8.5, color=GRAY)
    pg.insert_text((40, yb + 18), "แก้โดยแปลงทั้งเล่มเป็นภาพใน B2G_Repaired_Final.pdf", fontname="thb", fontsize=8.5, color=GRAY)
    p = os.path.join(ROOT, "output", "comparison_pdf", "B2G_Comparison.pdf")
    os.makedirs(os.path.dirname(p), exist_ok=True); out.save(p, deflate=True); print("comparison pdf:", p)


if __name__ == "__main__":
    qa_pdf(); comparison_pdf()
