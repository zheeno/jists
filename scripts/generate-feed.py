#!/usr/bin/env python3
"""Regenerate feed.json and sync article media into post front matter."""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

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
    "google_news_finance": "Finance",
    "google_news_geopolitics": "Geopolitics",
    "google_news_popculture": "Culture",
}

FEATURED_IMAGE_PATTERN = re.compile(
    r"^!\[[^\]]*\]\(https?://(?:picsum\.photos|images\.unsplash\.com|pixabay\.com|source\.unsplash\.com)[^)]*\)\s*\n?",
    re.MULTILINE,
)


def load_media_library() -> dict[str, dict[str, str]]:
    if not MEDIA_PATH.exists():
        return {}
    return json.loads(MEDIA_PATH.read_text(encoding="utf-8"))


def is_stock_image(url: str | None) -> bool:
    if not url:
        return True
    host = urlparse(url).netloc.lower()
    return any(
        bad in host
        for bad in ("unsplash.com", "picsum.photos", "pixabay.com", "source.unsplash.com")
    )


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
    slug_title: str,
    source: str,
    fm: dict[str, str],
    library: dict[str, dict[str, str]],
) -> dict[str, str]:
    curated = library.get(slug_title, {})
    category = (
        curated.get("category")
        or fm.get("category")
        or SOURCE_CATEGORY.get(source, "Tech")
    )
    source_url = curated.get("sourceUrl") or fm.get("sourceUrl") or ""

    # Prefer source-article / curated images over Unsplash stock.
    candidates = [
        curated.get("imageUrl"),
        fm.get("imageUrl"),
    ]
    image_url = next((url for url in candidates if url and not is_stock_image(url)), "")
    image_alt = ""
    if image_url == curated.get("imageUrl"):
        image_alt = curated.get("imageAlt") or ""
    if not image_alt:
        image_alt = fm.get("imageAlt") or ""

    return {
        "imageUrl": image_url,
        "imageAlt": image_alt,
        "category": category,
        "sourceUrl": source_url,
    }


def strip_embedded_featured_images(body: str) -> str:
    return FEATURED_IMAGE_PATTERN.sub("", body).lstrip("\n")


def slugify_category(name: str) -> str:
    slug = name.lower().replace(" & ", "-").replace(" ", "-").replace("&", "").replace(".", "")
    return re.sub(r"[^a-z0-9-]", "", slug)


def serialize_front_matter(fm: dict[str, str]) -> str:
    order = [
        "layout",
        "title",
        "date",
        "source",
        "sourceUrl",
        "category",
        "author",
        "readTime",
        "feedUrl",
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

            if key == "category":
                lines.append("categories:")
                lines.append(f"  - {value}")
                seen.add("categories")

    for key, value in fm.items():
        if key in seen or not value:
            continue
        if '"' not in value:
            lines.append(f'{key}: "{value}"')
        else:
            lines.append(f"{key}: {value}")

    lines.append("---")
    return "\n".join(lines)


def sync_post_file(md: Path, slug: str, media: dict[str, str], fm: dict[str, str], body: str) -> None:
    fm["layout"] = fm.get("layout", "post")
    fm["category"] = media["category"]
    fm["author"] = fm.get("author", AUTHOR)
    fm["readTime"] = estimate_read_time(body)
    fm["feedUrl"] = slug_to_url(slug)

    if media.get("sourceUrl"):
        fm["sourceUrl"] = media["sourceUrl"]

    if media.get("imageUrl"):
        fm["imageUrl"] = media["imageUrl"]
        fm["imageAlt"] = media.get("imageAlt") or fm.get("imageAlt") or ""
    else:
        # Drop stock Unsplash URLs so the site uses the editorial image fallback.
        if is_stock_image(fm.get("imageUrl")):
            fm.pop("imageUrl", None)
            fm.pop("imageAlt", None)

    cleaned_body = strip_embedded_featured_images(body)
    md.write_text(serialize_front_matter(fm) + "\n\n" + cleaned_body.lstrip("\n"), encoding="utf-8")


def main() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "clean-post-headings.py")],
        check=True,
    )

    library = load_media_library()
    items = []
    posts = sorted(POSTS_DIR.glob("*.md"), reverse=True)

    for md in posts:
        text = md.read_text(encoding="utf-8")
        fm, body = parse_front_matter(text)
        slug = md.stem
        _, _, _, title_slug = slug_parts(slug)
        source = fm.get("source", "newsletter")
        media = resolve_media(title_slug, source, fm, library)

        sync_post_file(md, slug, media, fm, body)

        item = {
            "title": fm.get("title", slug),
            "url": slug_to_url(slug),
            "date": fm.get("date", ""),
            "source": source,
            "category": media["category"],
            "categorySlug": slugify_category(media["category"]),
            "author": fm.get("author", AUTHOR),
            "readTime": estimate_read_time(body),
            "excerpt": extract_excerpt(body),
            "imageUrl": media.get("imageUrl") or "",
            "imageAlt": media.get("imageAlt") or "",
        }
        if media.get("sourceUrl"):
            item["sourceUrl"] = media["sourceUrl"]
        items.append(item)

    FEED_PATH.write_text(json.dumps({"items": items}, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {len(items)} posts and wrote {FEED_PATH}")


if __name__ == "__main__":
    main()
