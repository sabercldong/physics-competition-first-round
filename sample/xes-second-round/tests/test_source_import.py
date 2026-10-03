"""A new answer figure must not inflate the number of original illustrations."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import import_inventory
from quality import sha256


class SourceImport(unittest.TestCase):
    def test_source_exercise_has_one_identity_and_multiple_typed_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp).resolve()
            (book / "chapters").mkdir()
            (book / "reviews").mkdir()
            source = book / "source.pdf"
            source.write_bytes(b"source placeholder")
            (book / "preview.jpg").write_bytes(b"manually inspected fixture")
            (book / "sources.json").write_text(json.dumps({"sources": [{
                "source_id": "autumn_student_2020", "path": str(source)}]}))
            page = {"source_id": "autumn_student_2020", "physical_page": 1}
            (book / "page_inventory.jsonl").write_text(json.dumps(page) + "\n")
            (book / "chapters/ch01.tex").write_text(
                r"\label{r2ch01:pr:001}\label{r2ch01:fig:001}\label{r2ch01:eq:001}")
            obj = {"id": "p01", "object_type": "exercise", "source_number": "1",
                   "source_locator": "upper page", "description": "source question",
                   "target_id": "r2ch01:pr:001", "additional_targets": [
                       {"target_id": "r2ch01:fig:001", "target_object_type": "figure",
                        "notes": "explanation figure added in solution"},
                       {"target_id": "r2ch01:eq:001", "target_object_type": "formula",
                        "notes": "derived formula, not a separate source equation"}]}
            manifest = book / "reviews/page.json"
            manifest.write_text(json.dumps({
                "source_id": "autumn_student_2020", "source_sha256": sha256(source),
                "independent_visual_inventory": True, "pages": [{
                    "physical_page": 1, "printed_page": 1, "classification": "teaching",
                    "inspected_render": "preview.jpg", "objects": [obj]}]}))
            with patch.object(import_inventory, "BOOK", book):
                import_inventory.merge(manifest)
                # Reimport is idempotent.
                import_inventory.merge(manifest)
            inventory = import_inventory.load_rows(book / "source_inventory.jsonl")
            ledger = import_inventory.load_rows(book / "source_ledger.jsonl")
            self.assertEqual(len(inventory), 1)
            self.assertEqual(len(ledger), 3)
            self.assertEqual(len({r["source_object_id"] for r in ledger}), 1)
            self.assertTrue(all(r["object_type"] == "exercise" for r in ledger))
            self.assertNotIn("target_object_type", ledger[0])
            self.assertNotIn("mapping_role", ledger[0])
            self.assertEqual([r["target_object_type"] for r in ledger[1:]],
                             ["figure", "formula"])
            self.assertTrue(all(r["mapping_role"] == "extension" for r in ledger[1:]))
            self.assertEqual(len(import_inventory.load_rows(
                book / "page_inventory.jsonl")[0]["object_ids"]), 1)


if __name__ == "__main__":
    unittest.main()
