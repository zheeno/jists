# Hermes Article Style Guide

**Audience:** Hermes agent (upstream article generator)  
**Target site:** Jekyll newsletter at `zheeno/jists`  
**Last updated:** August 2026

Use this document as the **system prompt appendix** or **generation instructions** for Hermes when writing markdown files that land in `_posts/`.

---

## Golden rule

**Never add inline CSS.** All visual styling is handled by `assets/editorial.css` inside the `.editorial-content` wrapper. Generated markup must be semantic HTML + editorial class names only.

---

## Required front matter

Every post file must start with YAML front matter:

```yaml
---
layout: post
title: "Human-readable article title"
date: 2026-08-01
source: hackernews
---
```

| Field | Required | Notes |
|-------|----------|-------|
| `layout` | Yes | Always `post` |
| `title` | Yes | Shown in article header — do not repeat as `#` in body |
| `date` | Yes | `YYYY-MM-DD` |
| `source` | Yes | One of: `hackernews`, `newsletter`, `producthunt`, `googletrends`, `google_news_finance`, `google_news_geopolitics`, `google_news_popculture` |
| `category` | Optional | Synced by `generate-feed.py` if omitted |
| `sourceUrl` | Strongly recommended | Canonical URL of the original source article (used for Open Graph images) |
| `imageUrl` / `imageAlt` | Optional | Prefer the source article's OG image. **Never use Unsplash/Picsum.** Synced by `scripts/resolve-source-images.py` + `generate-feed.py` |

After import, the publishing pipeline runs:

```bash
python3 scripts/clean-post-headings.py
python3 scripts/generate-feed.py
```

---

## Section headings (critical)

### ✅ Correct — HTML with class, no inline styles

```html
<h2 class="editorial-h2" id="what-changed">What changed</h2>
```

```html
<h3 class="editorial-h3" id="suggested-fit-for-this-issue">Suggested fit for this issue</h3>
```

- Use **kebab-case** `id` values derived from the heading text.
- Headings render as serif type with a hairline rule above — warm paper editorial theme.

### ❌ Wrong — legacy inline styles (do not generate)

```html
<h2 class="editorial-h2" id="what-changed" style="display:block;margin:1.6rem 0;...;background:rgba(147,197,253,.22);color:#ffffff;...">What changed</h2>
```

These blue/purple boxed headings are from an **old dark-theme template**. They break the current editorial design (white text on light background, colored boxes).

### ❌ Wrong — markdown `##` for main sections

```markdown
## What changed
```

Markdown `##` headings do not receive `.editorial-h2` styling. Use the HTML pattern above for all section breaks.

### ❌ Wrong — duplicate article title

```markdown
# My Article Title
```

The post layout already renders `title` from front matter. Do not add an `#` h1 at the top of the body (except weekly digest intros — see below).

---

## Article templates

### Template A — Standard trend article

Use for individual Hacker News / news trend pieces.

**Opening** (two short paragraphs, plain markdown):

```markdown
In practice, **{Topic}** matters because it changes what you can ship—faster, with fewer failure modes, or with better economics.

But trends only feel "obvious" after the first wave of adoption. Before that, teams usually miss the tradeoffs.
```

**Sections** (fixed order, HTML headings):

1. `What changed`
2. `Why it matters now`
3. `The hidden constraint`
4. `Key takeaways` (bullet list)
5. `A simple plan for the next 24–72 hours` (numbered list)
6. `Sponsor Spotlight (Paid Partnership)`
7. `Suggested fit for this issue` (use `<h3 class="editorial-h3">`)

**Example section block:**

```html
<h2 class="editorial-h2" id="what-changed">What changed</h2>

This trend is getting attention because it changes the economics of one of three things: **how people build**, **how people decide**, or **how teams ship**.
```

### Template B — Weekly trend digest (`source: newsletter`)

```markdown
# This Week's Top Trends

*Curated from Google Trends + Hacker News + Product Hunt — {Month Day, Year}*

---

<h2 class="editorial-h2" id="1-article-slug-kebab">1. Article title here</h2>

**Source:** hackernews — **Virality Score:** 95/100

[Read full analysis →](https://example.com/article-url)

---

<h2 class="editorial-h2" id="sponsor-spotlight-paid-partnership">Sponsor Spotlight (Paid Partnership)</h2>
```

Number each trend entry. Use `editorial-h2` with **no inline styles**.

### Template C — Long-form editorial

For in-depth pieces, use descriptive section titles with the same HTML pattern:

```html
<h2 class="editorial-h2" id="why-progressive-web-components-matter-now">Why Progressive Web Components Matter Now</h2>
```

---

## Body content rules

| Element | Format |
|---------|--------|
| Paragraphs | Plain markdown |
| Emphasis | `**bold**` or `*italic*` |
| Lists | `-` bullets or `1)` numbered |
| Links | `[text](url)` |
| Horizontal rules | `---` between digest entries only |
| Code | `` `inline` `` or fenced blocks |
| Blockquotes | `>` markdown syntax |
| Images | Prefer `sourceUrl` so the pipeline can fetch the source OG image. Do **not** use Unsplash/Picsum. Do not embed `![...]` heroes in the body. |

### Do not generate

- `style=""` on any tag
- `class` attributes other than `editorial-h2` and `editorial-h3` on headings
- `![Featured image](...)` or `picsum.photos` URLs in the body
- `source.unsplash.com` random image URLs in the body
- Colored backgrounds, borders, or font-size overrides on headings
- HTML `<div>`, `<span>`, or wrapper elements for styling

---

## Reference: correct heading markup

Copy this verbatim pattern for every section heading:

```html
<h2 class="editorial-h2" id="why-it-matters-now">Why it matters now</h2>
```

```html
<h3 class="editorial-h3" id="suggested-fit-for-this-issue">Suggested fit for this issue</h3>
```

**Nothing else on the tag.** No `style`, no extra classes, no `font-weight`, no `background`, no `border-left`.

---

## Reference: posts that follow this guide

Good examples in `_posts/`:

- `2026-07-31-gemini-robotics-2-brings-whole-body-intelligence-to-robots.md`
- `2026-07-31-the-session-you-cannot-take-with-you.md`
- `2026-08-01-progressive-web-components.md`
- `2026-07-31-weekly-trend-digest-july-31-2026.md`

---

## Hermes prompt snippet

Paste this block into the Hermes agent system instructions:

```
When generating Jekyll newsletter markdown for zheeno/jists:

1. Use layout: post front matter with title, date, and source.
2. Section headings MUST be HTML: <h2 class="editorial-h2" id="kebab-id">Title</h2>
3. Subsections use: <h3 class="editorial-h3" id="kebab-id">Title</h3>
4. NEVER add style="" attributes or inline CSS to any element.
5. NEVER use markdown ## for section headings.
6. Include sourceUrl pointing at the original article. Do NOT use Unsplash/Picsum image URLs.
7. Do NOT include # title or embedded featured images in the body.
8. Only write files under _posts/. Never overwrite index.html, feed.json, or assets/.
9. Follow docs/HERMES_ARTICLE_STYLE.md in the jists repo for full templates.
```

---

## Do not modify site infrastructure files

Hermes should **only** write or update files in `_posts/`. Never overwrite:

- `index.html`, `categories.html`, or other layout/page files
- `feed.json` (regenerated by `scripts/generate-feed.py` from `_posts/`)
- `assets/*.js`, `assets/*.css`, or `_includes/*`

After importing new posts, run `python3 scripts/generate-feed.py` to rebuild the homepage feed.

---

Before writing output files, verify:

- [ ] No `style="` appears anywhere in the file
- [ ] All section headings use `<h2 class="editorial-h2" id="...">`
- [ ] Sponsor sub-heading uses `<h3 class="editorial-h3" id="...">`
- [ ] No `![` image markdown in body
- [ ] No `#` h1 duplicate of front matter title (except digest intro)
- [ ] Front matter includes `layout`, `title`, `date`, `source`
