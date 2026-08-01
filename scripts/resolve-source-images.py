#!/usr/bin/env python3
"""Resolve source article URLs and fetch Open Graph images into article-media.json."""

from __future__ import annotations

import html
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"
MEDIA_PATH = ROOT / "data" / "article-media.json"
CACHE_PATH = ROOT / "data" / "source-image-cache.json"

UA = "Mozilla/5.0 (compatible; JistsBot/1.0; +https://zheeno.github.io/jists/)"
SSL_CTX = ssl.create_default_context()

# Prefer these when digests use Google News redirects or HN search is noisy.
SOURCE_URL_OVERRIDES = {
    "elevators": "https://john.fun/elevators",
    "qm-multiplayer-agent-harness-for-work": "https://github.com/yc-software/qm",
    "google-fixed-more-chrome-bugs-in-june-than-over-the-past-two-years-thanks-to-ai": (
        "https://blog.google/security/chrome-stronger-with-every-update/"
    ),
    "the-session-you-cannot-take-with-you": "https://earendil.com/posts/session-portability/",
    "stacked-prs-are-now-live-on-github": (
        "https://github.blog/changelog/2026-07-30-stacked-pull-requests-are-now-in-public-preview/"
    ),
    "deepseek-v4-flash-update": "https://api-docs.deepseek.com/updates/",
    "gemini-robotics-2-brings-whole-body-intelligence-to-robots": (
        "https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/"
    ),
    "i-flagged-two-research-papers-for-fake-authors-and-both-were-accepted-as-orals": (
        "https://geospatialml.com/posts/reviewing-ai-slop/"
    ),
    "civil-war-in-sudan-global-conflict-tracker-council-on-foreign-relations": (
        "https://www.cfr.org/global-conflict-tracker/conflict/power-struggle-sudan"
    ),
    "progressive-web-components": "https://arielsalminen.com/2026/progressive-web-components/",
    "june-in-servo-real-world-compat-media-queries-sharedworker-and-more": (
        "https://servo.org/blog/2026/07/31/june-in-servo/"
    ),
    "getting-25-gbps-thunderbolt-ethernet-on-my-mac-studio": (
        "https://www.jeffgeerling.com/blog/2026/getting-25g-ethernet-mac-thunderbolt/"
    ),
    "bmw-spider-man-in-car-advertising": "https://consumerrights.wiki/w/BMW_Spider-Man_in-car_advertising",
    "read-this-before-you-buy-that-tv-streaming-stick": (
        "https://krebsonsecurity.com/2026/07/read-this-before-you-buy-that-tv-streaming-stick/"
    ),
    "lieber-studies-indo-pacific-volume-prisoners-of-war-and-a-taiwan-conflict-lieber-institute-west-point": (
        "https://lieber.westpoint.edu/"
    ),
    "neon-genesis-evangelion-is-coming-to-the-criterion-channel-in-september-complex": (
        "https://www.complex.com/"
    ),
    "run-kimi-k3-using-29-gb-of-ram-at-0-50-tok-s": "https://github.com/sqliteai/waste",
}

DIGEST_ENTRY_PATTERN = re.compile(
    r'<h2 class="editorial-h2" id="\d+-([^"]+)"[^>]*>.*?</h2>\s*.*?'
    r"\[Read full analysis →\]\((https?://[^)]+)\)",
    re.IGNORECASE | re.DOTALL,
)

OG_PATTERNS = [
    re.compile(r'<meta[^>]+property=["\']?og:image(?::url)?["\']?[^>]+content=["\']([^"\']+)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']?og:image(?::url)?["\']?', re.I),
    re.compile(r'<meta[^>]+name=["\']?twitter:image(?::src)?["\']?[^>]+content=["\']([^"\']+)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']?twitter:image(?::src)?["\']?', re.I),
]

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".svg")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def is_stock_image(url: str | None) -> bool:
    if not url:
        return True
    host = urlparse(url).netloc.lower()
    return any(bad in host for bad in ("unsplash.com", "picsum.photos", "pixabay.com", "source.unsplash.com"))


def title_slug_from_filename(slug: str) -> str:
    parts = slug.split("-", 3)
    return parts[3] if len(parts) >= 4 else slug


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.index("---", 3)
    fm: dict[str, str] = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip().strip('"')
    return fm


def extract_digest_urls() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for md in POSTS_DIR.glob("*weekly-trend-digest*.md"):
        text = md.read_text(encoding="utf-8")
        for match in DIGEST_ENTRY_PATTERN.finditer(text):
            title_slug = match.group(1)
            url = match.group(2).strip()
            if "news.google.com" in url:
                continue
            mapping[title_slug] = url
    return mapping


def hn_lookup(title: str) -> str | None:
    query = urllib.parse.urlencode({"query": title, "tags": "story", "hitsPerPage": 5})
    url = f"https://hn.algolia.com/api/v1/search?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as response:
            data = json.load(response)
    except Exception:
        return None

    title_l = title.lower().strip()
    for hit in data.get("hits") or []:
        hit_title = (hit.get("title") or "").lower().strip()
        hit_url = hit.get("url")
        if not hit_url:
            continue
        if hit_title == title_l or title_l in hit_title or hit_title in title_l:
            return hit_url
    return None


def fetch_html(url: str) -> tuple[str | None, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20, context=SSL_CTX) as response:
            return response.read(500_000).decode("utf-8", "ignore"), response.geturl()
    except Exception:
        return None, url


def looks_like_image(url: str) -> bool:
    path = urlparse(url).path.lower()
    if any(path.endswith(ext) for ext in IMAGE_EXTS):
        return True
    # Common CDN image paths without extensions
    return any(token in path for token in ("/image", "/images/", "/img/", "/og/", "/unfurl", "social-card", "twitter-card"))


def extract_og_image(page_html: str, base_url: str) -> str | None:
    for pattern in OG_PATTERNS:
        match = pattern.search(page_html)
        if not match:
            continue
        candidate = html.unescape(match.group(1).strip())
        if not candidate or candidate.startswith("data:"):
            continue
        absolute = urljoin(base_url, candidate)
        if absolute.rstrip("/") == base_url.rstrip("/"):
            continue
        if looks_like_image(absolute) or absolute.startswith("http"):
            if "unsplash.com" in absolute:
                continue
            return absolute

    # Fallback: first content image on the page.
    for match in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', page_html, re.I):
        absolute = urljoin(base_url, html.unescape(match.group(1).strip()))
        if looks_like_image(absolute) and "unsplash.com" not in absolute:
            return absolute
    return None


def resolve_image(source_url: str, cache: dict[str, str]) -> str | None:
    cached = cache.get(source_url)
    if cached and not is_stock_image(cached):
        return cached

    page_html, final_url = fetch_html(source_url)
    if not page_html:
        return None

    image = extract_og_image(page_html, final_url)
    if image:
        cache[source_url] = image
    return image


def main() -> None:
    media = load_json(MEDIA_PATH, {})
    cache = load_json(CACHE_PATH, {})
    digest_urls = extract_digest_urls()
    updated = 0

    for md in sorted(POSTS_DIR.glob("*.md")):
        title_slug = title_slug_from_filename(md.stem)
        if "weekly-trend-digest" in title_slug:
            # Digests keep a publication-style image; skip source fetch.
            continue

        text = md.read_text(encoding="utf-8")
        fm = parse_front_matter(text)
        title = fm.get("title", title_slug)
        source = fm.get("source", "")

        entry = dict(media.get(title_slug, {}))
        source_url = (
            entry.get("sourceUrl")
            or SOURCE_URL_OVERRIDES.get(title_slug)
            or digest_urls.get(title_slug)
            or (hn_lookup(title) if source == "hackernews" else None)
        )
        if not source_url:
            print(f"SKIP {title_slug} (no sourceUrl)")
            continue

        entry["sourceUrl"] = source_url
        if "category" not in entry and title_slug in media:
            entry["category"] = media[title_slug].get("category")

        current_image = entry.get("imageUrl")
        if is_stock_image(current_image):
            fetched = resolve_image(source_url, cache)
            if fetched:
                entry["imageUrl"] = fetched
                entry["imageAlt"] = entry.get("imageAlt") or f"Image from source: {title}"
                updated += 1
                print(f"OK   {title_slug}")
                print(f"     {fetched}")
            else:
                print(f"MISS {title_slug} ({source_url})")
        else:
            print(f"KEEP {title_slug}")

        media[title_slug] = entry

    MEDIA_PATH.write_text(json.dumps(media, indent=2) + "\n", encoding="utf-8")
    CACHE_PATH.write_text(json.dumps(cache, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {updated} media entries → {MEDIA_PATH}")


if __name__ == "__main__":
    main()
