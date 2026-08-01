#!/usr/bin/env python3
"""Regenerate feed.json from _posts front matter."""

import json
import re
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent.parent / "_posts"
FEED_PATH = Path(__file__).resolve().parent.parent / "feed.json"


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.index("---", 3)
    fm = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, text[end + 3 :]


def slug_to_url(slug: str) -> str:
    parts = slug.split("-", 3)
    if len(parts) >= 4:
        return f"{parts[0]}/{parts[1]}/{parts[2]}/{parts[3]}.html"
    return f"{slug}.html"


def extract_excerpt(body: str) -> str:
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("![") or line.startswith("#") or line.startswith("<"):
            continue
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        if len(text) > 160:
            return text[:160] + "…"
        return text
    return ""


def main() -> None:
    items = []
    for md in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        text = md.read_text(encoding="utf-8")
        fm, body = parse_front_matter(text)
        slug = md.stem
        items.append(
            {
                "title": fm.get("title", slug),
                "url": slug_to_url(slug),
                "date": fm.get("date", ""),
                "source": fm.get("source", "newsletter"),
                "excerpt": extract_excerpt(body),
            }
        )
    FEED_PATH.write_text(json.dumps({"items": items}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} items to {FEED_PATH}")


if __name__ == "__main__":
    main()
