+++
title = "winniemethmann.com — from WordPress to Astro"
date = 2026-04-19
slug = "winniemethmann-com-astro-portfolio"
description = "Migrating winniemethmann.com from WordPress to Astro: content collections, Sharp + AVIF images, bilingual i18n, 70% smaller build."

[taxonomies]
tags = ["astro", "wordpress-migration", "static-site", "sharp", "avif", "i18n", "food-photography", "portfolio"]

[extra]
summary = "A 10-year-old WordPress portfolio rebuilt in Astro: content collections instead of a CMS, Sharp-powered AVIF images, bilingual i18n, and a 70% smaller build."
faq = [
  { q = "Can a non-technical owner still edit the site?", a = "Yes, for copy. Editing Markdown in a GitHub web editor is, in practice, easier than the WordPress block editor. For new portfolio projects, the workflow is: drag images into a folder, write a short front-matter block, commit. If that's too technical, a one-page admin (Decap CMS, Sveltia CMS, or Keystatic) can be bolted on." },
  { q = "What about SEO after the migration?", a = "URLs were kept as-is wherever possible. Missing old paths redirect via Cloudflare rules. The sitemap is regenerated on every build, and structured data (Person, ImageGallery, Article) is emitted per page." },
  { q = "Why Astro and not Hugo?", a = "Hugo is faster and simpler for pure blogging, but Astro's typed content collections and first-class Image component won this case. For x2q.net itself, I later went with Zola — but for a portfolio with a heavy image pipeline, Astro remained the better fit." },
  { q = "How do images stay organised?", a = "Each portfolio project owns its own folder. The Git repo is the CMS. git log tells you when an image was added and why." },
  { q = "Is the build deterministic?", a = "Yes. Given the same inputs, the output is byte-for-byte identical. Sharp is pinned in package.json; so is Astro. CI runs on Node LTS." },
]
+++

**TL;DR —** [winniemethmann.com](https://winniemethmann.com) is the portfolio of a Danish food photographer and recipe developer. It was a WordPress site for a decade. I rebuilt it on [Astro](https://astro.build), using **content collections** (typed Markdown) instead of a CMS, **Sharp + AVIF** for the image pipeline, and **Astro's i18n routing** (Danish default, English at `/en/`). Build time: ~30 seconds. Output size: ~70% smaller. No more admin panel, no more plugin updates, no more bot-probed login endpoint.

## Why move off WordPress

For a portfolio that changes a few times a month, WordPress was doing too much work:

- **PHP runtime and MySQL** for a site that is functionally static.
- **Dozens of plugins** for image galleries, contact forms, SEO, caching — each with its own update cadence and security disclosures.
- **A half-forked theme** that had accumulated patches nobody remembered why.
- **An admin login endpoint** that was probed several thousand times a day by bots.
- **Regular caching headaches** every time the CDN and the plugins disagreed.

Concretely, dropping WordPress meant:

- **No admin panel to keep patched.** WordPress core releases, plugin updates, theme updates — gone.
- **No database.** Content lives as Markdown in the repo.
- **No login surface for bots to probe.** There's no `/wp-admin/` anymore.
- **~10× faster page loads** with no caching layer required.
- **~70% smaller total build size**, swapping hand-exported JPEGs for AVIF at sensible `srcset` breakpoints.

The tradeoff is that non-technical editing goes away. In practice that did not matter: the site owner was happier editing Markdown than fighting the WordPress block editor.

## Why Astro

I considered Hugo, 11ty, Next.js static export, and SvelteKit. Astro won on three specific points:

1. **Content collections.** A typed, schema-checked way to describe a portfolio project as a directory of photos plus some front-matter. Build fails loudly if anything is malformed. No CMS required.
2. **The `<Image>` component.** Astro's built-in image pipeline handles AVIF + JPEG fallback + `srcset` + `width`/`height` attributes with a one-liner. Sharp is the engine under the hood.
3. **Islands architecture, not relevant here.** The site has no interactive components, so it ships basically zero JavaScript.

## Content collections, not a CMS

Each portfolio project is a directory under `src/content/portfolio/` with a front-matter schema:

```
src/content/portfolio/
├── 2024-cookbook-editorial/
│   ├── index.mdx
│   ├── cover.jpg
│   ├── 01.jpg, 02.jpg, …
└── 2023-spring-catalogue/
    ├── index.mdx
    ├── cover.jpg
    └── 01.jpg …
```

`index.mdx` front-matter declares the project title, category, year, and cover image. Astro enforces the schema at build time via [`defineCollection`](https://docs.astro.build/en/guides/content-collections/) with a Zod schema. If a project is missing a cover image or has a bad category, the build fails.

Categories used: **food photography, recipe development, interior & garden styling, editorial, cookbooks, and fashion**. Adding a new project is `mkdir` + `cp *.jpg` + a short YAML front-matter block. No admin UI, no database migration, no cache to invalidate.

## Image pipeline: Sharp + AVIF

Food photography lives or dies on image quality. Astro's `<Image>` component, powered by [Sharp](https://sharp.pixelplumbing.com/), generates:

- **AVIF** as the primary format. Roughly all modern browsers support it now (see [caniuse](https://caniuse.com/avif)).
- **JPEG** fallback with matching `srcset` breakpoints (320, 640, 960, 1280, 1920 px).
- Explicit `width` and `height` attributes, so there is zero cumulative layout shift while images load.
- `loading="lazy"` for below-the-fold images and `fetchpriority="high"` for the hero.

**Numbers**: a typical portfolio page went from ~4.8 MB of hand-exported JPEGs to ~1.4 MB of AVIF — about a 70% reduction — with no visible quality loss at typical display sizes.

## i18n — Danish default, English at /en/

Astro's i18n routing sits in `astro.config.mjs`:

```js
export default defineConfig({
  i18n: {
    defaultLocale: "da",
    locales: ["da", "en"],
    routing: { prefixDefaultLocale: false },
  },
});
```

That gives:

- `/` for Danish (the default, no prefix).
- `/en/` for English.
- Each content entry declares its language via its collection and filename.
- `<link rel="alternate" hreflang>` and the sitemap are generated from the same source.

Posts and portfolio entries that lack a translation simply don't appear in the other locale's routing — they don't 404 to a wrong-language page.

## Deployment and build

- **Output**: fully static, deployed as plain files behind Cloudflare.
- **Build time**: ~30 seconds on a cold cache, ~6 seconds incrementally.
- **No server, no database, no runtime cost.**

## Measurable outcomes

| Metric | WordPress (before) | Astro (after) |
| --- | --- | --- |
| Build / deploy time | n/a (instant publish) | ~30s cold, ~6s warm |
| Typical page size (portfolio page) | ~4.8 MB | ~1.4 MB |
| Largest Contentful Paint | ~2.8 s | ~0.9 s |
| Time to Interactive | ~3.5 s | ~1.1 s |
| JS shipped | ~220 KB | ~0 KB |
| Plugins to keep patched | 14 | 0 |

## FAQ

### Can a non-technical owner still edit the site?

Yes, for copy. Editing Markdown in a GitHub web editor is, in practice, easier than the WordPress block editor. For new portfolio projects, the workflow is: drag images into a folder, write a short front-matter block, commit. If that's too technical, a one-page admin (Decap CMS / Sveltia CMS / Keystatic) can be bolted on.

### What about SEO after the migration?

URLs were kept as-is wherever possible. Missing old paths redirect via Cloudflare rules. The sitemap is regenerated on every build, and structured data (`Person`, `ImageGallery`, `Article`) is emitted per page.

### Why Astro and not Hugo?

Hugo is faster and simpler for pure blogging, but Astro's typed content collections and first-class `<Image>` component won this case. For [x2q.net](https://www.x2q.net) itself, I later went with Zola — for a portfolio with a heavy image pipeline, Astro remained the better fit.

### How do images stay organised?

Each portfolio project owns its own folder. The Git repo is the CMS. `git log` tells you when an image was added and why.

### Is the build deterministic?

Yes. Given the same inputs, the output is byte-for-byte identical. Sharp is pinned in `package.json`; so is Astro. CI runs on Node LTS.

If you're on a WordPress site that's doing far less than its infrastructure suggests, Astro is worth the afternoon it takes to try.
