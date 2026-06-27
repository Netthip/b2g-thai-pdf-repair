# -*- coding: utf-8 -*-
"""
Regression tests for the audit pipeline and Thai validation helpers.

Run: python -m pytest tests/ -q   (or: python tests/test_thai_text_validation.py)
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

THAI_RE = re.compile(r"[฀-๿]")
# Floating/duplicated mark patterns that indicate corruption
DUP_MARK_RE = re.compile(r"[ัิ-ฺ็-๎]{2,}")  # 2+ stacked upper/lower marks
LEADING_MARK_RE = re.compile(r"(^|\s)[ัิ-ฺ็-๎]")  # mark with no base


def has_thai(s):
    return bool(THAI_RE.search(s))


def suspicious_marks(s):
    """Return True if string shows stacked marks or a mark without a base consonant."""
    return bool(DUP_MARK_RE.search(s) or LEADING_MARK_RE.search(s))


class TestThaiHelpers(unittest.TestCase):
    def test_has_thai(self):
        self.assertTrue(has_thai("ปฏิรูป"))
        self.assertFalse(has_thai("CITIZENS BUDGET 2570"))

    def test_correct_word_not_suspicious(self):
        self.assertFalse(suspicious_marks("การปฏิรูปกฎหมาย"))

    def test_stacked_marks_flagged(self):
        # two tone/vowel marks in a row -> corruption signal
        self.assertTrue(suspicious_marks("กิิ"))

    def test_leading_mark_flagged(self):
        self.assertTrue(suspicious_marks(" ิรูป"))


class TestArtifacts(unittest.TestCase):
    def test_baseline_lock_exists(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "data", "baseline_lock.json")))

    def test_registry_exists(self):
        self.assertTrue(os.path.exists(
            os.path.join(ROOT, "data", "issue_registry", "issue_registry.csv")))

    def test_page_count_locked_72(self):
        import json
        base = json.load(open(os.path.join(ROOT, "data", "baseline_lock.json"), encoding="utf-8"))
        self.assertEqual(base["page_count"], 72)


if __name__ == "__main__":
    unittest.main(verbosity=2)
