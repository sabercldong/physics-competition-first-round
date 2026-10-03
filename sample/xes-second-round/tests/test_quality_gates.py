import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import audit
import build
import quality
import release
import render_review


class QualityGates(unittest.TestCase):
    def test_silent_math_command_and_control_character_errors(self):
        self.assertTrue(audit.tex_typo_errors(r"$F=sum_j v_j$"))
        self.assertTrue(audit.tex_typo_errors("$x=\x0crac{1}{2}$"))
        self.assertTrue(audit.tex_typo_errors(r"$x,qquad y$"))
        self.assertTrue(audit.tex_typo_errors(r"$q^{,2}$"))
        self.assertTrue(audit.tex_typo_errors(r"$x Longrightarrow y$"))
        self.assertEqual(audit.tex_typo_errors(r"$F=\sum_j v_j,\quad x=\frac12$"), [])

    def test_chapter_assets_only_invalidate_owners_or_explicit_consumers(self):
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            (book / "chapters").mkdir()
            (book / "assets/ch02").mkdir(parents=True)
            (book / "style.tex").write_text("Shared style", encoding="utf-8")
            image = book / "assets/ch02/apparatus.png"
            image.write_bytes(b"image")
            chapter = book / "chapters/ch01.tex"
            chapter.write_text("No image", encoding="utf-8")
            self.assertNotIn(image, quality.input_paths([{"number": 1}], book))
            self.assertIn(image, quality.input_paths([{"number": 2}], book))
            chapter.write_text(r"\includegraphics[width=4cm]{assets/ch02/apparatus.png}", encoding="utf-8")
            self.assertIn(image, quality.input_paths([{"number": 1}], book))

    def test_main_contract_excludes_advanced(self):
        jobs = build.main_jobs(build.load_book())
        self.assertEqual(len(jobs), 34)
        self.assertEqual(len({j["output_name"] for j in jobs}), 34)
        self.assertEqual(len(jobs[-1]["chapters"]), 28)
        self.assertFalse(any(c.get("kind") == "advanced" for j in jobs for c in j["chapters"]))
        self.assertEqual(jobs[-1]["output_name"], "高中物理竞赛二轮讲义.pdf")

    def test_main_metadata_has_title_without_promotional_suffix(self):
        tex = build.wrapper("", [], True)
        self.assertIn("pdftitle={高中物理竞赛二轮讲义}", tex)
        for term in ("完整精修", "含解答与解图", "\\includepdf"):
            self.assertNotIn(term, tex)

    def test_equal_total_answers_does_not_hide_missing_answer(self):
        text = r"""\begin{examplebox}{A}\end{examplebox}
        \begin{practicebox}{B}\begin{solution}b\end{solution}
        \begin{solution}b again\end{solution}\end{practicebox}"""
        errors = audit.question_errors(text)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("有0个" in e for e in errors))
        self.assertTrue(any("有2个" in e for e in errors))

    def test_orphan_solution_fails(self):
        self.assertTrue(audit.question_errors(r"\begin{solution}unassigned\end{solution}"))

    def test_one_answer_for_each_type(self):
        self.assertEqual(audit.question_errors(r"""
          \begin{examplebox}{A}\begin{solution}a\end{solution}\end{examplebox}
          \begin{practicebox}{B}\begin{solution}b\end{solution}\end{practicebox}
        """), [])

    def test_old_artifact_cannot_survive_source_or_pdf_change(self):
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            (book / "chapters").mkdir()
            (book / "tools").mkdir()
            for name in ("style.tex", "book.json", "tools/build.py", "chapters/ch01.tex"):
                (book / name).write_text("initial", encoding="utf-8")
            work = book / "build/chapter-01"
            work.mkdir(parents=True)
            (work / "main.pdf").write_bytes(b"test artifact")
            data = {"items": [{"number": 1}], "successful_compile_passes": 2,
                    "pdf_sha256": quality.sha256(work / "main.pdf"),
                    "inputs": quality.fingerprints([{"number": 1}], book)}
            quality.write_json(work / "artifact.json", data)
            self.assertEqual(quality.artifact_errors(work, book), [])
            (book / "chapters/ch01.tex").write_text("changed", encoding="utf-8")
            self.assertTrue(any("源文件已变更" in e for e in quality.artifact_errors(work, book)))
            (work / "main.pdf").write_bytes(b"different PDF")
            self.assertTrue(any("PDF与构建记录不一致" in e for e in quality.artifact_errors(work, book)))

    def test_missing_human_review_fails_even_if_pdf_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            work = book / "build/chapter-01"
            work.mkdir(parents=True)
            (work / "main.pdf").write_bytes(b"exists")
            errors = quality.review_errors(work, book)
            self.assertTrue(any("缺本轮人工审阅记录" in e for e in errors))

    def test_missing_inventory_does_not_become_zero_omissions(self):
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            quality.write_json(book / "sources.json", {"sources": []})
            errors = quality.source_inventory_errors(book)
            self.assertTrue(any("source_inventory.jsonl" in e for e in errors))
            self.assertTrue(any("page_inventory.jsonl" in e for e in errors))

    def test_editing_review_evidence_invalidates_review(self):
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            (book / "reviews").mkdir()
            work = book / "build/chapter-01"
            work.mkdir(parents=True)
            evidence = book / "reviews/observations.md"
            evidence.write_text("specific observations", encoding="utf-8")
            record = {"status": "verified", "inputs": {}, "pdf_sha256": "PDF",
                      "unresolved_findings": [], "checks": {}}
            for category in ("page_layout", "figures", "physics", "source_completeness", "pdf_structure"):
                record["checks"][category] = {"status": "passed",
                    "evidence": ["reviews/observations.md"],
                    "evidence_sha256": {"reviews/observations.md": quality.sha256(evidence)}}
            quality.write_json(work / "artifact.json", {"inputs": {}, "pdf_sha256": "PDF"})
            quality.write_json(book / "reviews/chapter-01.json", record)
            with patch.object(quality, "artifact_errors", return_value=[]):
                self.assertEqual(quality.review_errors(work, book), [])
                evidence.write_text("different observations", encoding="utf-8")
                self.assertTrue(any("内容已变更" in e for e in quality.review_errors(work, book)))

    def test_excluded_page_still_requires_independent_review(self):
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            source = book / "source.pdf"
            source.write_bytes(b"source")
            quality.write_json(book / "sources.json", {"sources": [{
                "source_id": "autumn_student_2020", "path": str(source), "pages": 1}]})
            page = {"source_id": "autumn_student_2020", "physical_page": 1,
                    "source_sha256": quality.sha256(source), "classification": "excluded",
                    "exclusion_reason": "blank", "object_ids": [],
                    "object_inventory_verified": False}
            (book / "page_inventory.jsonl").write_text(json.dumps(page) + "\n", encoding="utf-8")
            for filename in ("source_inventory.jsonl", "source_ledger.jsonl"):
                (book / filename).write_text("", encoding="utf-8")
            self.assertTrue(any("1个源页" in e for e in quality.source_inventory_errors(book)))
            page["object_inventory_verified"] = True
            (book / "page_inventory.jsonl").write_text(json.dumps(page) + "\n", encoding="utf-8")
            self.assertEqual(quality.source_inventory_errors(book), [])

    def test_release_block_does_not_call_publish(self):
        with patch.object(sys, "argv", ["release.py", "--publish"]), \
             patch.object(release, "preflight", return_value=["review unfinished"]), \
             patch.object(release, "publish") as publish:
            with self.assertRaises(SystemExit) as error:
                release.main()
            self.assertEqual(error.exception.code, 1)
            publish.assert_not_called()

    def test_new_pdf_render_does_not_leave_old_pages_in_current_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            target = work / "render"
            target.mkdir()
            quality.write_json(target / "manifest.json", {"pdf_sha256": "oldhash"})
            (target / "page-099.png").write_bytes(b"old page")
            current = render_review.prepare_render_directory(work, "newhash")
            self.assertEqual(current, target)
            self.assertFalse((current / "page-099.png").exists())
            self.assertEqual((work / "render-history/oldhash/page-099.png").read_bytes(), b"old page")


if __name__ == "__main__":
    unittest.main()
