# www.x2q.net

Personal blog. Built with [Zola](https://www.getzola.org/).

## Local

```sh
zola serve
```

Open http://127.0.0.1:1111/ (EN) and http://127.0.0.1:1111/da/ (DA).

```sh
zola build
```

Outputs to `public/`.

## Deploy (Cloudflare Pages)

**Build command:** `zola build`
**Build output directory:** `public`
**Environment variables:**

- `ZOLA_VERSION=0.22.1`

The `static/_headers` file sets HSTS, CSP, Permissions-Policy, and the right content-types for `llms.txt` / `sitemap.xml` in production.

## Layout

- `content/` — posts (default lang) and `*.da.md` translations
- `templates/` — Tera templates (`base.html`, `index.html`, `page.html`, `section.html`, `partials/`)
- `static/` — CSS, favicon, `_headers`, `CNAME`, `llms.txt`, `apple-touch-icon.png`, `robots.txt`
- `config.toml` — Zola config (multilingual en/da, taxonomies, feeds)
- `i18n` strings live under `[translations]` / `[languages.da.translations]` in `config.toml`

## Adding a post

```sh
# English (default lang)
cat > content/post/my-post.md <<'EOF'
+++
title = "My post title"
date = 2026-04-22
slug = "my-post"
description = "SEO meta description, ~155 chars."

[taxonomies]
tags = ["tag1", "tag2"]

[extra]
summary = "Shown on the homepage + post list."
+++

Body…
EOF

# Danish translation (same slug recommended)
cp content/post/my-post.md content/post/my-post.da.md
# …translate title/description/body…
```
