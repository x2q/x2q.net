#!/usr/bin/env python3
"""Generate per-page Open Graph cards (1200x630) for x2q.

One card per post slug (Danish + English translations share a slug, so they
share a card). Plus a site-wide cards/index.png used for the home page,
section listings, and tag pages.

Reads each content/post/*.md front-matter for `title` and `slug` (falling back
to the filename when no explicit slug is set). Cards are checked into
static/cards/ — rerun this script only when titles change or posts are added:

    python3 scripts/social_cards.py
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "post"
OUT = ROOT / "static" / "cards"

# Brand tokens (mirror static/css/style.css :root)
PAPER = "#f3f6f3"
INK = "#0a2a1d"
INK_MUTED = "#466055"
ACCENT = "#0f7a47"

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

TAGLINE = "notes on tech, food, and everything in between"


def frontmatter(text):
    m = re.search(r"^\+\+\+\s*\n(.*?)\n\+\+\+", text, re.DOTALL)
    return m.group(1) if m else ""


def field(fm, key):
    m = re.search(rf'^{key}\s*=\s*"(.*?)"\s*$', fm, re.MULTILINE)
    return m.group(1) if m else None


def slug_for(path, fm):
    explicit = field(fm, "slug")
    if explicit:
        return explicit
    # strip .md and any .<lang> suffix → matches Zola's default slug
    name = path.name
    name = re.sub(r"\.(md)$", "", name)
    name = re.sub(r"\.[a-z]{2}$", "", name)
    return name


def render(slug, title, subtitle, wordmark="X2Q"):
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{slug}.png"
    args = [
        "magick", "-size", "1200x630", f"xc:{PAPER}",
        # accent bar, top-left
        "-fill", ACCENT, "-draw", "rectangle 90,118 154,128",
        # wordmark
        "-font", FONT_BOLD, "-fill", INK, "-pointsize", "40",
        "-gravity", "northwest", "-annotate", "+90+150", wordmark,
        # title, auto-wrapped inside a fixed box
        "(", "-background", "none", "-fill", INK, "-font", FONT_BOLD,
        "-pointsize", "70", "-size", "1020x320", "-gravity", "west",
        f"caption:{title}", ")",
        "-gravity", "northwest", "-geometry", "+90+250", "-composite",
        # subtitle / tagline, bottom-left
        "-font", FONT_REG, "-fill", INK_MUTED, "-pointsize", "30",
        "-gravity", "southwest", "-annotate", "+90+70", subtitle,
        str(dest),
    ]
    subprocess.run(args, check=True)
    return dest


def main():
    seen = {}
    for path in sorted(POSTS.glob("*.md")):
        if path.stem.startswith("_index"):
            continue
        text = path.read_text(encoding="utf-8")
        fm = frontmatter(text)
        slug = slug_for(path, fm)
        if slug in seen:
            continue
        title = field(fm, "title") or slug
        seen[slug] = title
        render(slug, title, f"x2q.net  ·  {TAGLINE}")
        print(f"  cards/{slug}.png")

    # site-wide fallback for home, sections, tag pages
    render("index", "X2Q", TAGLINE, wordmark="online since 2002")
    print("  cards/index.png")
    print(f"Done: {len(seen) + 1} cards.")


if __name__ == "__main__":
    sys.exit(main())
