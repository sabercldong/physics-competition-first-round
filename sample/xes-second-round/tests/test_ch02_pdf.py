"""Current artifact checks; these do not replace a source/physics review."""
from pathlib import Path
import re
import sys
import unittest
import fitz

BOOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "tools"))
import quality
import release


class ChapterTwoPDF(unittest.TestCase):
    def test_current_pdf_structure_fonts_and_unicode(self):
        work = BOOK / "build/chapter-02"
        self.assertEqual(quality.artifact_errors(work), [])
        self.assertEqual(release.pdf_errors(work / "main.pdf", False), [])
        with fitz.open(work / "main.pdf") as doc:
            text = "".join(page.get_text() for page in doc)
            self.assertNotIn("\ufffd", text)
            self.assertNotIn("sumj", text.replace(" ", "").replace("\n", ""))
            for token in ("动力学", "布朗运动", "∫", "∑", "×", "√"):
                self.assertIn(token, text)
            self.assertEqual(len(re.findall(r"图\s*2\.\d+：", text)), 12)
            self.assertEqual([page.get_text().strip().splitlines()[-1]
                              for page in list(doc)[1:]],
                             [str(i) for i in range(1, len(doc))])
            for _, title, number in doc.get_toc():
                self.assertIn(title, doc[number-1].get_text().replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
