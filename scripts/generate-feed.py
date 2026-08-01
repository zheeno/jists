#!/usr/bin/env python3
"""Regenerate feed.json and sync article media into post front matter."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"
FEED_PATH = ROOT / "feed.json"
MEDIA_PATH = ROOT / "data" / "article-media.json"
AUTHOR = "Efezino Ukpowe"

SOURCE_CATEGORY = {
    "newsletter": "Digest",
    "hackernews": "Tech",
    "producthunt": "Products",
    "googletrends": "Trends",
}

FALLBACK_IMAGES = [
    {
        "imageUrl": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=80",
        "imageAlt": "Earth from orbit with city lights glowing at night",
    },
    {
        "imageUrl": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1600&q=80",
        "imageAlt": "Team of creators working across a long wooden table",
    },
    {
        "imageUrl": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1600&q=80",
        "imageAlt": "Laptop with code on a sunlit desk",
    },
]

FEATURED_IMAGE_PATTERN = re.compile(
    r"^!\[[^\]]*\]\(https?://(?:picsum\.photos|images\.unsplash\.com|pixabay\.com)[^)]*\)\s*\n?",
    re.MULTILINE,
)


def load_media_library() -> dict[str, dict[str, str]]:
    return json.loads(MEDIA_PATH.read_text(encoding="utf-8"))


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.index("---", 3)
    fm: dict[str, str] = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip().strip('"')
    return fm, text[end + 3 :]


def slug_parts(slug: str) -> tuple[str, str, str, str]:
    parts = slug.split("-", 3)
    if len(parts) >= 4:
        return parts[0], parts[1], parts[2], parts[3]
    return "", "", "", slug


def slug_to_url(slug: str) -> str:
    year, month, day, title = slug_parts(slug)
    if year and month and day:
        return f"{year}/{month}/{day}/{title}.html"
    return f"{slug}.html"


def extract_excerpt(body: str, limit: int = 180) -> str:
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("![") or line.startswith("#") or line.startswith("<"):
            continue
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        if len(text) > limit:
            return text[: limit - 1].rstrip() + "…"
        return text
    return ""


def estimate_read_time(body: str) -> str:
    words = len(re.findall(r"\w+", body))
    minutes = max(1, math.ceil(words / 220))
    return f"{minutes} min read"


def resolve_media(
    slug_title: str, source: str, index: int, library: dict[str, dict[str, str]]
) -> dict[str, str]:
    curated = library.get(slug_title)
    if curated:
        return {
            "imageUrl": curated["imageUrl"],
            "imageAlt": curated["imageAlt"],
            "category": curated.get("category") or SOURCE_CATEGORY.get(source, "Tech"),
        }

    fallback = FALLBACK_IMAGES[index % len(FALLBACK_IMAGES)]
    return {
        "imageUrl": fallback["imageUrl"],
        "imageAlt": fallback["imageAlt"],
        "category": SOURCE_CATEGORY.get(source, "Tech"),
    }


def strip_embedded_featured_images(body: str) -> str:
    return FEATURED_IMAGE_PATTERN.sub("", body).lstrip("\n")


def serialize_front_matter(fm: dict[str, str]) -> str:
    order = [
        "layout",
        "title",
        "date",
        "source",
        "category",
        "author",
        "readTime",
        "imageUrl",
        "imageAlt",
        "description",
    ]
    lines = ["---"]
    seen: set[str] = set()

    for key in order:
        if key in fm and fm[key]:
            value = fm[key]
            if key in {"title", "imageAlt", "description"} and '"' not in value:
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f"{key}: {value}")
            seen.add(key)

    for key, value in fm.items():
        if key in seen or not value:
            continue
        if '"' not in value:
            lines.append(f'{key}: "{value}"')
        else:
            lines.append(f"{key}: {value}")

    lines.append("---")
    return "\n".join(lines)


def sync_post_file(md: Path, media: dict[str, str], fm: dict[str, str], body: str) -> None:
    fm["layout"] = fm.get("layout", "post")
    fm["category"] = media["category"]
    fm["author"] = fm.get("author", AUTHOR)
    fm["imageUrl"] = media["imageUrl"]
    fm["imageAlt"] = media["imageAlt"]
    fm["readTime"] = estimate_read_time(body)

    cleaned_body = strip_embedded_featured_images(body)
    md.write_text(serialize_front_matter(fm) + "\n\n" + cleaned_body.lstrip("\n"), encoding="utf-8")


def main() -> None:
    library = load_media_library()
    items = []
    posts = sorted(POSTS_DIR.glob("*.md"), reverse=True)

    for index, md in enumerate(posts):
        text = md.read_text(encoding="utf-8")
        fm, body = parse_front_matter(text)
        slug = md.stem
        _, _, _, title_slug = slug_parts(slug)
        source = fm.get("source", "newsletter")
        media = resolve_media(title_slug, source, index, library)

        sync_post_file(md, media, fm, body)

        items.append(
            {
                "title": fm.get("title", slug),
                "url": slug_to_url(slug),
                "date": fm.get("date", ""),
                "source": source,
                "category": media["category"],
                "author": fm.get("author", AUTHOR),
                "readTime": estimate_read_time(body),
                "excerpt": extract_excerpt(body),
                "imageUrl": media["imageUrl"],
                "imageAlt": media["imageAlt"],
            }
        )

    FEED_PATH.write_text(json.dumps({"items": items}, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {len(items)} posts and wrote {FEED_PATH}")


if __name__ == "__main__":
    main()
