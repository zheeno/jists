#!/usr/bin/env python3
"""Remove inline style attributes from editorial heading tags in _posts."""

from __future__ import annotations

import re
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent.parent / "_posts"

# Strip inline styles from editorial heading tags (legacy Hermes output).
STYLE_PATTERN = re.compile(r'(<h[23][^>]*class="editorial-h[23]"[^>]*)\s+style="[^"]*"([^>]*>)')


def clean_text(text: str) -> str:
    return STYLE_PATTERN.sub(r"\1\2", text)


def clean_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    cleaned = clean_text(text)
    if cleaned != text:
        path.write_text(cleaned, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for md in sorted(POSTS_DIR.glob("*.md")):
        if clean_file(md):
            changed += 1
            print(f"Cleaned: {md.name}")
    print(f"Done. Updated {changed} files.")


if __name__ == "__main__":
    main()
