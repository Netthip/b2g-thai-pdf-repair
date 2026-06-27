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

### ขั้นต่อไป
- (กิ๊ฟ) แก้ TH-001 ใน Canva ตาม CANVA_FIX_GUIDE.md → export PDF ใหม่ → ส่งกลับ
- (จีโฮ) รัน 03/04 ยืนยัน TH-001 หาย + ไม่มี regression → ผ่าน Quality Gate
- เพิ่มหน้า branding ท้ายเล่ม (ฉบับ branding แยกจากฉบับทางการ)
