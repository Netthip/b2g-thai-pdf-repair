# Changelog

## [Unreleased]

### Round 1 — Audit ต้นฉบับ (2026-06-27)
- ล็อก baseline ของไฟล์ต้นฉบับ (SHA-256, 72 หน้า, deps, ฟอนต์)
- render ครบ 72 หน้า @150 DPI + dump text layer (ยืนยันว่า mojibake)
- ตรวจเต็มหน้าครบ 1–72
- ซูมยืนยัน: สารบัญ, ย่อหน้า GDP, หัวเรื่องหมวดทั้ง 5
- **พบข้อผิดพลาดยืนยันแล้ว 1 รายการ: TH-001** (หัวเรื่องหน้า 66 "การปฏิรูปกฎหมาย" เพี้ยน)
- ออก Issue Registry (CSV/XLSX/MD) + audit summary + ตารางตรวจรายหน้า
- บันทึก Human Review Required 2 รายการ

### Round 2 — ซูมหัวข้อทุกจุด (2026-06-27)
- ดึงบรรทัดหัวข้อ/แถบสี ≥18pt ทั้งเล่ม = 365 บรรทัด → contact sheets (`scripts/round2_heading_crops.py`)
- ซูมตรวจครบทั้ง 365 บรรทัด: **พบเพี้ยน 1 = TH-001** เท่านั้น; ที่เหลือถูกต้องทั้งหมด
- ปิด HR-002 (หัวข้อ SME ถูกต้อง — รอบ 1 อ่านผิดที่ความละเอียดต่ำ)
- พยายามเข้าแก้ Canva ผ่าน MCP: ดีไซน์ DAHKRmbPj74 = "Not allowed" (บัญชีเชื่อมต่อไม่ใช่เจ้าของ)
  → ต้องแชร์สิทธิ์ edit ให้ vistriter@gmail.com หรือเจ้าของแก้เองตาม CANVA_FIX_GUIDE.md

### Round 3 — พิสูจน์อักษร body ด้วย OCR (2026-06-27)
- ดาวน์โหลด tha.traineddata; OCR ทั้ง 72 หน้า (tesseract tha+eng) → `data/ocr/`
- ตรวจพจนานุกรม pythainlp (`scripts/07_body_ocr_proofread.py`): 464 flag → 277 คำจริง →
  94 token เหลือ → ตรวจครบ = OCR เพี้ยนของคำที่ถูกต้องทั้งหมด → **body 0 errors**
- ปิด HR-001 (body) และ HR-002 (SME) → Human Review คงค้าง = 0
- สรุป: ทั้งเล่มมีข้อผิดพลาดจริงจุดเดียว = TH-001

### Round 4 — พบปัญหาสระลอย (renderer-dependent) + ซ่อมทั้งเล่ม (2026-06-27)
- ผู้ใช้รายงาน + ส่งภาพหน้าจอจริง (หน้า 7 'ปัญหา'→'ปั ญ') → พบ **DISPLAY-001**:
  สระ/วรรณยุกต์ลอยทับตัวถัดไปบน viewer มือถือ/เว็บ ทั้งเล่ม (MuPDF/Adobe แสดงถูก จึงหลุดรอบ 1-3)
- ยืนยัน Canva MCP เข้า design DAHKRmbPj74 ไม่ได้ (เจ้าของคนละบัญชี) แม้ให้สิทธิ์บัญชี ai.netthip แล้ว
- **สร้าง B2G_Repaired_Final.pdf**: rasterize 72 หน้า @180 DPI (วางสระถูก) → image-based →
  สระไม่ลอยทุก viewer; + overlay แก้ TH-001 หน้า 66 เบคเป็นภาพ (`scripts/08_build_image_pdf.py`)
- QA: 72 หน้า, live-text=0, หน้า 66 ถูกต้อง → ออก B2G_QA_Final_Report + B2G_Comparison
  (`scripts/09_build_qa_and_comparison.py`)

### ขั้นต่อไป
- (ผู้ใช้) ทดสอบเปิด B2G_Repaired_Final.pdf บนมือถือจริง ยืนยันสระไม่ลอย
- ถ้าต้องการฉบับ text select ได้/accessibility → แชร์ Canva design ให้ ai.netthip แล้วแก้ที่ต้นฉบับ
- เพิ่มหน้า branding ท้ายเล่ม (แยกฉบับ branding กับฉบับทางการ)
