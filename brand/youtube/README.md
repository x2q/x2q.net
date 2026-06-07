# X2Q — YouTube brand assets

On-brand imagery for the X2Q YouTube channel, matching the site's racing-green
identity (same wordmark as `static/favicon.svg`).

| File | Size | Use | YouTube spec |
|------|------|-----|--------------|
| `avatar.png` | 800×800 | Channel profile picture | ≥98×98, PNG, square (shown as a circle) |
| `banner.png` | 2560×1440 | Channel banner / art | Google-recommended 2560×1440 (min 2048×1152), ≤6 MB; all-device safe area is the centred **1546×423** |
| `description.txt` | — | Channel "About" text (EN + DA) | ≤1000 chars per language |

Sources are the `.svg` files; the `.png`s are rendered from them. All text and
copy is laid out inside the banner's 1546×423 safe area so nothing is clipped
on mobile.

## Regenerate

```sh
cd brand/youtube
rsvg-convert -w 800  -h 800  avatar.svg -o avatar.png
rsvg-convert -w 2560 -h 1440 banner.svg -o banner.png
```

Palette (mirrors `static/css/style.css`): paper `#f3f6f3`, racing-green ink
`#0a2a1d`, emerald accent `#3fcf8e`. Wordmark font falls back to Georgia (serif)
so it renders without the site's Fraunces webfont.
