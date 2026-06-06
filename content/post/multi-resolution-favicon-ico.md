+++
title = "Create a real multi-resolution favicon.ico (2026)"
date = 2013-01-13
updated = 2026-06-06
slug = "multi-resolution-favicon-ico"
description = "Build a crisp multi-resolution favicon.ico (16/32/48px) from one source image with ImageMagick or GIMP, and pair it with a modern SVG favicon and apple-touch-icon."

[taxonomies]
tags = ["favicon", "favicon-ico", "imagemagick", "svg", "web", "seo"]

[extra]
summary = "A single 16×16 favicon looks pixelated in bookmarks and tabs. A .ico file can hold several resolutions at once — here's how to bake 16/32/48px into one favicon.ico, plus the modern SVG + apple-touch-icon setup that goes alongside it."
+++

**TL;DR —** a `.ico` file can contain *multiple* image sizes in one file. Render 16/32/48px PNGs from a high-res source and combine them: `magick 16.png 32.png 48.png favicon.ico`. Then add a modern `favicon.svg` and an `apple-touch-icon.png` for everything else.

> This first went up here in 2013 with GIMP-by-hand instructions. The multi-resolution `.ico` trick still matters, but in 2026 the command-line route is faster and an **SVG favicon** does most of the heavy lifting — both are below.

## Why multi-resolution

Most favicons are exported at a single 16×16 resolution. That looks fine in a tab but pixelated when a browser scales it up — bookmarks bars, the address bar on hi-DPI screens, pinned tabs, OS shortcuts. Browsers ask for different sizes (16, 32, 48…), and the `.ico` container can hold all of them in one file, so the browser picks the best fit.

## The command-line way (ImageMagick)

Start from a square source image, **at least 256×256**. Rasterize the sizes you want, then pack them into one `.ico`.

From a PNG source:

```
magick source.png -resize 16x16   /tmp/16.png
magick source.png -resize 32x32   /tmp/32.png
magick source.png -resize 48x48   /tmp/48.png
magick /tmp/16.png /tmp/32.png /tmp/48.png favicon.ico
```

ImageMagick's own SVG rasterizer is flaky — if your source is an SVG, render the PNGs with `rsvg-convert` first, then combine:

```
rsvg-convert -w 16 -h 16 logo.svg -o /tmp/16.png
rsvg-convert -w 32 -h 32 logo.svg -o /tmp/32.png
rsvg-convert -w 48 -h 48 logo.svg -o /tmp/48.png
magick /tmp/16.png /tmp/32.png /tmp/48.png favicon.ico
```

Verify the `.ico` really contains all three sizes:

```
magick identify favicon.ico
favicon.ico[0] ICO 16x16 ...
favicon.ico[1] ICO 32x32 ...
favicon.ico[2] ICO 48x48 ...
```

## The GIMP way (no ImageMagick)

1. Open your square, high-res source in GIMP.
2. **Image → Canvas Size** to make it perfectly square if it isn't.
3. **Image → Scale Image** to 48×48, then **Layer → Duplicate** and scale copies to 32×32 and 16×16, so you have one layer per size.
4. **File → Export As → `favicon.ico`**. GIMP writes each layer as a resolution inside the single `.ico`.

## The modern half: SVG + apple-touch-icon

In 2026 the `.ico` is the legacy fallback. Modern browsers prefer a crisp, scalable **SVG favicon**, and iOS wants a PNG **apple-touch-icon**. Ship all three:

```
rsvg-convert -w 180 -h 180 -b "#fff" logo.svg -o apple-touch-icon.png
```

Then in your `<head>`:

```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

The `sizes="32x32"` hint on the `.ico` tells modern browsers "there's something better here" so they reach for the SVG, while older ones fall back to the multi-resolution `.ico`.

## FAQ

### Do I still need favicon.ico if I have an SVG?

Yes, as a fallback. Older browsers and a lot of link-preview/scraper bots only look for `/favicon.ico` at the site root, so keep it there.

### What sizes should the .ico contain?

16, 32, and 48 cover essentially everything in practice. You *can* add 64 and 128, but they mostly just inflate the file — the SVG handles large sizes better.

### Why does my favicon not update?

Browsers cache favicons aggressively. Hard-refresh, or append a one-off query string while testing (`/favicon.ico?v=2`).

## Summary

- A `.ico` holds multiple sizes; bake in 16/32/48 with `magick 16.png 32.png 48.png favicon.ico`.
- Rasterize SVG sources with `rsvg-convert` first (ImageMagick's SVG support is unreliable).
- Pair the `.ico` with a modern `favicon.svg` + `apple-touch-icon.png` and three `<link>` tags.
