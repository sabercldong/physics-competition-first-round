#!/usr/bin/env python3
"""Apply final cross-review corrections after all original quality overlays."""
from importlib import import_module
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
MODULES = [import_module(name) for name in (
    "quality_final_review_mechanics",
    "quality_final_review_thermal_fields",
    "quality_final_review_em_optics",
    "quality_final_review_advanced",
    "quality_final_review_layout",
)]


def apply(path, kind, key=None):
    old = text = path.read_text()
    for module in MODULES:
        function = getattr(module, kind, None)
        if function is not None:
            text = function(text) if key is None else function(key, text)
    if text != old:
        path.write_text(text)
        print(f"final reviewed {path.relative_to(BOOK)}")


if __name__ == "__main__":
    for number in range(1, 33):
        apply(BOOK / f"generated/chapters/ch{number:02d}.tex", "apply_chapter_revision", number)
    apply(BOOK / "generated/appendices/appendix-e.tex", "apply_appendix_revision")
    for path in sorted((BOOK / "advanced").glob("A*.tex")):
        apply(path, "apply_advanced_revision", path.name)
        apply(path, "apply_file_revision", path.name)
    apply(BOOK / "chapters/quality-20261023/em-optics/ch29-notes.tex", "apply_chapter_revision", 29)
    for name in ["style.tex", "advanced/layout.tex"]:
        apply(BOOK / name, "apply_file_revision", Path(name).name)
