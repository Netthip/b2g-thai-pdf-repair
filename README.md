# B2G — Thai PDF Repair & Evidence Pipeline

> **Auditable, reproducible repair of Thai-language errors in AI / Canva-generated PDFs.**

A quality-assurance pipeline that detects and fixes Thai typographic defects — floating
vowels & tone marks, glyph corruption, broken spacing — in a 72-page government
*Citizens' Budget* document, with **per-page evidence** and a **versioned audit trail**.

`render → audit → fix → QA → evidence`  ·  Fiscal Year 2570 (2027)  ·  72 pages  ·  public source

**Highlights**
- Detected floating Thai marks affecting ~8,022 words (renderer-dependent) → fixed for **all viewers** by high-DPI rasterization.
- Caught a corrupted section headline (`การปฏฐูป → การปฏิรูป`) that escaped full-page review; confirmed by font-span analysis.
- Full-document Thai proofread (OCR + dictionary) → **0 body-text errors**.
- Numbers left **untouched** (kept as source) — flagged in a review table, never guessed.
- Reproducible scripts, locked baseline (SHA-256), and a clean Git history as development evidence.

See **[docs/BRANCHING.md](docs/BRANCHING.md)** for the branching strategy.

---

ระบบตรวจสอบและซ่อมข้อผิดพลาดภาษาไทยในไฟล์ PDF ที่สร้างจากเครื่องมือออกแบบ/AI
แบบ **ตรวจสอบย้อนกลับได้ (auditable)** และ **ทำซ้ำได้ (reproducible)**

เอกสารที่ตรวจในรอบนี้: **`งบประมาณฉบับประชาชน ประจำปีงบประมาณ พ.ศ. 2570`** (72 หน้า, สร้างจาก Canva)

> **ที่มาเอกสารต้นฉบับ (สาธารณะ):** สำนักงบประมาณ — https://www.bb.go.th/topic-detail.php?id=18918
> เอกสารเป็นข้อมูลเปิดที่เผยแพร่/ดาวน์โหลดได้ จึงรวมไฟล์ต้นฉบับไว้ใน repo เป็นฐานหลักฐาน (baseline)

**ไฟล์ส่งมอบหลัก:** `output/final_delivery/B2G_Repaired_Final.pdf` (แก้ภาษาไทย/สระลอย, ตัวเลขคงต้นฉบับ) ·
`B2G_Repaired_Final_Branded.pdf` (ฉบับมีหน้าเครดิตท้ายเล่ม) · `B2G_Final_Error_List.xlsx` (ทุกแถวที่ผิด)

---

## ปัญหาที่พบใน PDF ภาษาไทยจาก AI / เครื่องมือออกแบบ

1. **Text layer เสีย (mojibake)** — ฟอนต์ถูกฝังแบบ subset โดยไม่มี ToUnicode map ที่ถูกต้อง
   การ extract ข้อความจึงได้ "ขยะ" ทำให้ **เทียบ diff ข้อความตรง ๆ ไม่ได้** ต้องตรวจจากภาพ render
2. **อักขระเพี้ยน / สระ-วรรณยุกต์หายหรือย้ายตำแหน่ง** ในบางหัวเรื่อง (เช่น ฟอนต์หัวเรื่องที่ไม่มีกลิฟไทยครบ
   ทำให้คลัสเตอร์ซับซ้อนอย่าง "ปฏิ" แตก) — มองข้ามง่ายเพราะดูเผิน ๆ เหมือนถูก

## วัตถุประสงค์

- ตรวจจับและบันทึกข้อผิดพลาดภาษาไทยทุกหน้า แบบมีหลักฐานรายหน้า/รายจุด
- จัดทำรายการแก้ไขที่ trace กลับไป Issue ID ได้
- ส่งมอบหลักฐาน QA และแพ็กเกจที่ขึ้น GitHub เป็นหลักฐานการพัฒนางานได้

## ขอบเขต (สำคัญ — อ่านก่อน)

เอกสารต้นฉบับเป็น **งานออกแบบอินโฟกราฟิก Canva** (รูป กราฟ ไอคอน เลย์เอาต์อิสระ)
แนวทางที่เลือกคือ **Audit-driven correction**: ระบบตรวจ + ออก Issue Registry ที่แม่นยำ →
**แก้ที่ Canva (ต้นฉบับ)** เพื่อคงความสมบูรณ์ของงานออกแบบ 100% → export ใหม่ → ระบบ QA ซ้ำ
(ไม่ rebuild เลย์เอาต์ใหม่ด้วยโค้ด เพราะจะทำให้คุณภาพงานออกแบบตก)

## ขั้นตอนการตรวจ (Pipeline)

| สคริปต์ | หน้าที่ |
|---|---|
| `scripts/01_extract_pdf.py` | render ทุกหน้าเป็น PNG (150 DPI) + dump text layer (mojibake) |
| `scripts/02_detect_thai_issues.py` | สร้าง Issue Registry (CSV/XLSX/MD) + audit summary จากผลตรวจสายตา |
| `scripts/03_generate_repaired_document.py` | (หลังแก้ Canva) รับ PDF ที่ export ใหม่เข้าสู่ pipeline เปรียบเทียบ |
| `scripts/04_render_and_compare.py` | เทียบภาพหน้าเดิม↔ใหม่ หาส่วนที่หาย/เปลี่ยน |
| `scripts/05_visual_qa.py` | สร้างตารางตรวจรายหน้า (page-by-page) |
| `scripts/06_build_final_package.py` | รวมโค้ด+รายงาน เป็น GitHub package zip |

## วิธีรัน

```bash
python -m pip install -r requirements.txt
python scripts/01_extract_pdf.py --dpi 150     # render + extract
python scripts/02_detect_thai_issues.py        # build issue registry + summary
python scripts/05_visual_qa.py                 # page-by-page table
```

## โครงสร้าง repository

```
input/original_pdf/      ไฟล์ต้นฉบับ (ไม่ขึ้น public — ดู .gitignore)
data/page_images/        ภาพ render รายหน้า (หลักฐานการตรวจ)
data/crops/              ภาพซูมจุดที่ตรวจ
data/issue_registry/     Issue Registry (CSV/MD) + audit_summary.json
data/baseline_lock.json  baseline ที่ล็อก (hash, จำนวนหน้า, เวอร์ชัน, ฟอนต์)
output/audit_reports/    รายงาน XLSX + หลักฐานภาพ (evidence/)
docs/                    scope, methodology, QA, changelog, Canva fix guide
```

## ข้อจำกัดของการตรวจอัตโนมัติ

- ไม่มี text layer ที่ใช้ได้ → ตรวจจากภาพ จึงพึ่งสายตา/ซูม (และ OCR ถ้าต้องการ)
- การตรวจเต็มหน้า 150 DPI จับ "ความผิดปกติเชิงโครงสร้าง" ได้ดี แต่ **อักขระเพี้ยนระดับกลิฟ
  อาจหลุดได้** (กรณี TH-001 หลุดจากการตรวจเต็มหน้า จับได้ตอนซูม) → จึงต้องมี **รอบ 2 ซูมหัวข้อทุกแถบ**
  และ/หรือ **พิสูจน์อักษรโดยมนุษย์** ก่อนรับรอง 0

## การแยก "Human Review Required"

ทุกจุดที่ยืนยันไม่ได้ 100% จะถูกบันทึกในชีต **HumanReview** ของ Issue Registry
ห้ามนับเป็น "ผ่าน/0 errors" จนกว่าจะมีหลักฐานรายจุด — ดู `docs/quality_assurance.md`

## หลักการ

- ไม่เดาคำไทยที่ไม่แน่ใจ → mark เป็น Human Review
- ไม่อ้าง "ตรวจครบ/ไม่มีข้อผิดพลาด" หากไม่มีหลักฐานรายหน้า
- ทุกการแก้ trace กลับ Issue ID ได้ / รันซ้ำ-ตรวจซ้ำได้

---

_B2G (Bo + Giho) · ตรวจแก้และทบทวนเนื้อหาโดย นางสาวเนตรทิพย์ GiftzaXBOHO_
