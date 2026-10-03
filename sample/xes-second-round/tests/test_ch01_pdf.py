"""Regression checks of the current internal PDF, not a content acceptance."""
from pathlib import Path
import sys
import unittest
import fitz

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "tools"))
import quality
import release


class ChapterOnePDF(unittest.TestCase):
    def test_current_build_has_embedded_unicode_fonts_and_valid_pdf(self):
        work = BOOK / "build/chapter-01"
        self.assertEqual(quality.artifact_errors(work), [])
        self.assertEqual(release.pdf_errors(work / "main.pdf", False), [])

    def test_chinese_and_math_symbols_are_copyable(self):
        with fitz.open(BOOK / "build/chapter-01/main.pdf") as doc:
            text = "".join(p.get_text() for p in doc)
        self.assertNotIn("\ufffd", text)
        for token in ("运动学", "旋轮线", "∫", "×", "∑", "√"):
            self.assertTrue(token in text, f"Expected source symbol is not copyable: {token}")
