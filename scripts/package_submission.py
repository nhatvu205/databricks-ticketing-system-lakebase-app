"""Create a clean source archive for the assignment submission."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "lakebase-support-ticketing-source.zip"
EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "htmlcov", "dist", "build"}
EXCLUDED_NAMES = {".env", ".coverage", OUTPUT.name}


def should_include(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return not (set(relative.parts) & EXCLUDED_PARTS or path.name in EXCLUDED_NAMES or path.suffix == ".pyc")


with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
    for path in ROOT.rglob("*"):
        if path.is_file() and should_include(path):
            archive.write(path, path.relative_to(ROOT))

print(f"Created {OUTPUT.name}")
