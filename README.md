# Efezino Ukpowe — Newsletter

A premium editorial newsletter site built with **Jekyll** and deployed to **GitHub Pages**. Daily trending analysis from Hacker News, Google Trends, and Product Hunt — written for founders, engineers, and curious readers who want practical takeaways.

**Live site:** [https://zheeno.github.io/jists/](https://zheeno.github.io/jists/)

---

## Table of contents

- [Overview](#overview)
- [Project structure](#project-structure)
- [Design system](#design-system)
- [Local development](#local-development)
- [Publishing workflow](#publishing-workflow)
- [Adding content](#adding-content)
- [GitHub Pages deployment](#github-pages-deployment)
- [Maintenance scripts](#maintenance-scripts)
- [Customization](#customization)

---

## Overview

| | |
|---|---|
| **Stack** | Jekyll 4, static HTML/CSS, vanilla JavaScript |
| **Styling** | Custom design tokens + editorial CSS (Libre Bodoni + Public Sans) |
| **Hosting** | GitHub Pages via GitHub Actions |
| **Content** | Markdown posts in `_posts/` with YAML front matter |
| **Feed** | `feed.json` powers the homepage archive grid |

The site uses a **typography-first editorial design**: serif headlines, clean sans-serif body text, asymmetric post grid with a featured story, and reading-optimized article layouts.

---

## Project structure

```
.
├── _config.yml              # Jekyll site configuration
├── _includes/
│   ├── head.html            # Meta tags, fonts, stylesheets
│   ├── subscribe.html       # Newsletter subscribe CTA
│   ├── footer.html          # Site footer
│   └── github-pages-script.html
├── _layouts/
│   ├── default.html         # Base HTML shell
│   └── post.html            # Article layout
├── _posts/                  # Newsletter issues (Markdown)
├── assets/
│   ├── tokens.css           # Design tokens (colors, type, spacing)
│   ├── site.css             # Shell layout, cards, navigation
│   ├── editorial.css        # Article body typography
│   ├── main.js              # Homepage feed loader + skeletons
│   ├── favicon.svg
│   └── logo.svg
├── scripts/
│   ├── generate-feed.py     # Regenerate feed.json from _posts
│   └── clean-post-headings.py
├── .github/workflows/
│   └── pages.yml            # CI/CD: build Jekyll → deploy Pages
├── index.html               # Homepage (Jekyll layout)
├── feed.json                # Post index for homepage JS
└── Gemfile                  # Ruby dependencies
```

---

## Design system

### Typography

| Role | Font | Usage |
|------|------|-------|
| Display | **Libre Bodoni** | Headlines, article titles, pull quotes |
| Body | **Public Sans** | Body copy, navigation, UI |
| Mono | **JetBrains Mono** | Dates, labels, code |

### Colors

Tokens are defined in `assets/tokens.css` and support **light** (default) and **dark** (via `prefers-color-scheme`):

| Token | Light | Purpose |
|-------|-------|---------|
| `--color-bg` | `#FAFAF8` | Warm paper background |
| `--color-ink` | `#0A0A0A` | Primary text |
| `--color-accent` | `#BE123C` | Links, hover states |
| `--color-rule` | `#E4E4E7` | Dividers, borders |

### Layout

- **Homepage:** 12-column asymmetric grid — featured post spans 7 columns, others span 5
- **Articles:** Max 68ch reading measure, serif section headings with hairline rules
- **Motion:** Subtle card lift on hover, skeleton loaders, `prefers-reduced-motion` respected

---

## Local development

### Prerequisites

- Ruby 3.x
- Bundler (`gem install bundler`)

### Setup

```bash
git clone https://github.com/zheeno/jists.git
cd jists
bundle install
```

### Run locally

```bash
bundle exec jekyll serve
```

Open [http://localhost:4000/jists/](http://localhost:4000/jists/) (note the `/jists` baseurl from `_config.yml`).

### Regenerate the post feed

After adding or editing posts in `_posts/`:

```bash
python3 scripts/generate-feed.py
```

Each feed item powers the homepage article cards and includes:

```json
{
  "title": "Elevators",
  "url": "2026/08/01/elevators.html",
  "date": "2026-08-01",
  "source": "hackernews",
  "category": "Infrastructure",
  "author": "Efezino Ukpowe",
  "readTime": "6 min read",
  "excerpt": "You ride in them every day without a second thought…",
  "imageUrl": "https://images.unsplash.com/photo-…",
  "imageAlt": "Glass elevator shafts rising through a modern atrium"
}
```

Curated Unsplash image mappings live in `data/article-media.json` — the single source of truth for article media. Running `generate-feed.py` syncs those values into each post's front matter (`imageUrl`, `imageAlt`, `category`) and regenerates `feed.json`, so landing cards and article pages always match.

### Clean inline heading styles

If generated posts include inline `style=""` on headings:

```bash
python3 scripts/clean-post-headings.py
```

---

## Publishing workflow

### 1. Add or edit a post

Create a file in `_posts/` with this naming convention:

```
YYYY-MM-DD-your-post-slug.md
```

Example front matter:

```yaml
---
layout: post
title: "Your Article Title"
date: 2026-08-01
source: hackernews
description: "Optional SEO description for meta tags."
---
```

Write content in Markdown. Use `##` for section headings — do **not** add inline styles. The `editorial.css` stylesheet handles all heading presentation.

### 2. Update the feed

```bash
python3 scripts/generate-feed.py
```

### 3. Commit and push to `main`

```bash
git add .
git commit -m "Add issue: Your Article Title"
git push origin main
```

GitHub Actions automatically builds and deploys to GitHub Pages.

---

## GitHub Pages deployment

Deployment is fully automated via `.github/workflows/pages.yml`.

### First-time setup

1. Go to **Settings → Pages** in the GitHub repo
2. Under **Build and deployment**, set **Source** to **GitHub Actions**
3. Push to `main` — the workflow builds Jekyll and deploys `_site`

### Manual trigger

You can also run the workflow from **Actions → Deploy GitHub Pages → Run workflow**.

### Site URL

With `baseurl: /jists` in `_config.yml`, the site is served at:

```
https://zheeno.github.io/jists/
```

To use a custom domain, add a `CNAME` file and update `_config.yml` `url` and `baseurl`.

---

## Maintenance scripts

| Script | Purpose |
|--------|---------|
| `scripts/generate-feed.py` | Build `feed.json` from all `_posts/*.md` files |
| `scripts/clean-post-headings.py` | Strip inline `style=""` from generated heading tags |

Run both after bulk content imports from the generation pipeline.

---

## Customization

### Subscribe CTA

Edit `_includes/subscribe.html`. Replace the mailto link with your email provider embed:

- [Buttondown](https://buttondown.com/)
- [Substack](https://substack.com/)
- [Mailchimp](https://mailchimp.com/)

### Brand colors

Edit CSS custom properties in `assets/tokens.css`. All shell and article styles inherit from these tokens.

### Fonts

Update the Google Fonts link in `_includes/head.html` and the `--font-*` variables in `tokens.css`.

### Base URL

If the repo is renamed or moved to a user site (`username.github.io`), update `_config.yml`:

```yaml
url: https://zheeno.github.io
baseurl: ""          # empty for user/org root site
# baseurl: /jists    # for project pages
```

---

## Content pipeline

This directory can be populated by an upstream generation pipeline (`../output/`). When importing generated posts:

1. Copy markdown files into `_posts/`
2. Run `python3 scripts/clean-post-headings.py`
3. Run `python3 scripts/generate-feed.py`
4. Commit and push

---

## License

Content © Efezino Ukpowe. Site code is MIT unless otherwise noted.
