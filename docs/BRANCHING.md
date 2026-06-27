# Branching Strategy

A lightweight GitFlow used to keep the repair work auditable and easy to review.

```
release tag (v1.0) ─┐
                    ▼
main ───────────────●        stable, released editions (tagged)
                     \
fy70 ─────────────────●       integration branch for the FY2570 (2027) edition
                       \
topic branches ─────────●     short-lived; opened as Pull Requests into `fy70`,
                              reviewed via diff, then merged
```

## Branches

| Branch | Purpose |
|---|---|
| `main` | Stable, released editions. Tagged (e.g. `v1.0`). |
| `fy70` | Integration branch for the Fiscal Year 2570 *Citizens' Budget* edition. |
| `audit/*` | Auditing the original document (baseline, issue registry). |
| `fix/*` | Corrections (Thai typography, headline, layout). |
| `docs/*` | Reports, methodology, roadmap, evidence. |
| `release/*` | Release preparation. |

## Workflow

1. Branch a topic branch off `fy70` (e.g. `fix/thai-typography`).
2. Commit focused changes; keep each branch single-purpose.
3. Open a **Pull Request** into `fy70` — review the **diff**.
4. Merge into `fy70`; when the edition is ready, merge `fy70` → `main` and tag a release.

## Naming examples

```
audit/fy70-baseline
fix/fy70-thai-floating-marks
fix/fy70-headline-th-001
docs/fy70-evidence
release/fy70-v1.0
```

---

แนวทางแตกกิ่ง (สรุปไทย): `main` = ฉบับเสถียร (ติด tag) · `fy70` = สายงานปีงบประมาณ 2570 ·
กิ่งย่อย `fix/* docs/* audit/*` = งานย่อย เปิด Pull Request เข้า `fy70` ดู diff แล้ว merge
