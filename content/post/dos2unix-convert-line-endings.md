+++
title = "Convert Windows line endings to Unix with dos2unix (2026)"
date = 2008-04-30
updated = 2026-06-06
slug = "dos2unix-convert-line-endings"
description = "Convert CRLF (DOS/Windows) line endings to LF (Unix) on Linux and macOS with dos2unix — install it, convert files in place, batch a whole tree, and the sed one-liner when it's missing."

[taxonomies]
tags = ["dos2unix", "line-endings", "linux", "macos", "command-line"]

[extra]
summary = "Windows uses CRLF line endings, Unix uses LF — and the mismatch breaks shell scripts, configs, and diffs. dos2unix converts them in place; on Debian/Ubuntu it's now its own package (no more tofrodos). Includes a recursive batch and a sed fallback."
+++

**TL;DR —** `dos2unix file.txt` rewrites a file's CRLF (Windows) line endings to LF (Unix) in place. Install it with `sudo apt install dos2unix`. No dos2unix? `sed -i 's/\r$//' file.txt` does the same.

> A 2008 note that pointed at the `tofrodos` package. On modern Debian/Ubuntu **`dos2unix` is its own package now** — simpler. The rest still applies: CRLF vs LF mismatches are a perennial nuisance.

## Why it matters

DOS/Windows ends each line with **CR+LF** (`\r\n`); Unix/Linux/macOS use just **LF** (`\n`). A file authored on Windows and run on Linux carries stray `\r` characters that cause:

- `#!/bin/bash^M: bad interpreter` when running a script.
- Configs and `.env` files where a value silently gains a trailing `\r`.
- Diffs and `grep` matching things that look identical but aren't.

## Install

```
sudo apt install dos2unix        # Debian / Ubuntu (its own package now)
sudo dnf install dos2unix         # Fedora
brew install dos2unix             # macOS
```

## Convert

```
dos2unix script.sh
```

It converts **in place**. Keep a copy under a new name if you want the original:

```
dos2unix -n script.sh script.unix.sh
```

The reverse exists too — `unix2dos file.txt` adds CRLF back (e.g. for a file a Windows tool insists on).

## Batch a whole tree

Convert every shell script under the current directory:

```
find . -type f -name '*.sh' -exec dos2unix {} +
```

`dos2unix` skips binary files it detects, so a broad `find . -type f` is usually safe — but scope it with `-name` when you can.

## No dos2unix installed? Use sed

Strip the trailing CR with `sed` (in place with `-i`):

```
sed -i 's/\r$//' file.txt
```

Or with `tr` (writes to a new file — `tr` can't edit in place):

```
tr -d '\r' < dosfile.txt > unixfile.txt
```

## Check what you've got

```
file script.sh
script.sh: Bourne-Again shell script, ASCII text, with CRLF line terminators
```

"with CRLF line terminators" is the tell. `cat -A file` shows `^M` at each line end.

## FAQ

### macOS sed says "invalid command code"

BSD `sed` (macOS) needs an argument after `-i`: `sed -i '' 's/\r$//' file.txt`. Or just `brew install dos2unix` and avoid the difference.

### Git keeps reintroducing CRLF

That's Git's `core.autocrlf` / `.gitattributes`, not the file itself. Set `* text=auto eol=lf` in `.gitattributes` to normalise on commit.

### Does this change the file's encoding too?

No — line endings and character encoding are independent. For UTF-8/Latin-1 conversion see [iconv](/post/convert-file-encoding-iconv/).

## Summary

- `dos2unix file` — CRLF → LF, in place. `unix2dos` for the reverse.
- Install: `sudo apt install dos2unix` (now its own package).
- Batch: `find . -name '*.sh' -exec dos2unix {} +`.
- Fallback: `sed -i 's/\r$//' file` (`sed -i '' …` on macOS).
