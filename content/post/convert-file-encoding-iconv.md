+++
title = "Convert a text file's character encoding with iconv (2026)"
date = 2007-02-24
updated = 2026-06-06
slug = "convert-file-encoding-iconv"
description = "Convert a text file between UTF-8 and ISO-8859-1 (or any encoding) with iconv on Linux/macOS — detect the current encoding, handle untranslatable characters, and batch-convert recursively."

[taxonomies]
tags = ["iconv", "encoding", "utf-8", "linux", "macos", "command-line"]

[extra]
summary = "iconv converts a text file from one character encoding to another. Detect what you have with file -i, convert with iconv -f FROM -t TO, and use //TRANSLIT or //IGNORE for characters the target charset can't represent. Includes a recursive batch one-liner."
+++

**TL;DR —** `iconv -f UTF-8 -t ISO-8859-1 in.txt > out.txt` converts encodings. Check what you've got first with `file -i in.txt`, and add `//TRANSLIT` (approximate) or `//IGNORE` (drop) for characters the target can't represent.

> A 2007 note — and the original even had the direction muddled, which is exactly the trap. `iconv` does nothing to *tell* you which way to go, so step one is always: find out what encoding you actually have.

## 1. Detect the current encoding

```
file -i mystery.txt
mystery.txt: text/plain; charset=utf-8
```

`file` guesses from the bytes — usually right for UTF-8 vs Latin-1, but a guess. If Danish `æ ø å` (or other non-ASCII) shows up garbled in your editor, the declared/assumed encoding is wrong.

## 2. Convert

The flags are **`-f` (from)** and **`-t` (to)**. Don't mix them up:

```
# UTF-8  ->  ISO-8859-1 (Latin-1)
iconv -f UTF-8 -t ISO-8859-1 utf.txt > latin1.txt

# ISO-8859-1  ->  UTF-8
iconv -f ISO-8859-1 -t UTF-8 latin1.txt > utf.txt
```

(The long forms `--from-code` / `--to-code` are identical.)

## 3. Handle characters the target can't represent

Converting *to* a narrow charset like ISO-8859-1 fails on characters it doesn't contain (€, em-dashes, emoji) with `illegal input sequence`. Two ways out:

```
# //TRANSLIT — approximate: “ ” -> " ", é -> e where needed
iconv -f UTF-8 -t ISO-8859-1//TRANSLIT in.txt > out.txt

# //IGNORE — silently drop characters that don't fit
iconv -f UTF-8 -t ISO-8859-1//IGNORE in.txt > out.txt
```

## Edit in place safely

`iconv in.txt > in.txt` truncates the file before reading it — you lose the data. Use a temp file:

```
iconv -f ISO-8859-1 -t UTF-8 in.txt > in.tmp && mv in.tmp in.txt
```

## Batch-convert a tree

Convert every `.txt` under a directory from Latin-1 to UTF-8:

```
find . -type f -name '*.txt' -exec sh -c \
  'iconv -f ISO-8859-1 -t UTF-8 "$1" > "$1.utf8" && mv "$1.utf8" "$1"' _ {} \;
```

List everything `iconv` supports with `iconv -l`.

## FAQ

### iconv says "illegal input sequence at position N"

The real source encoding isn't what you told `-f`, or you're converting to a charset that can't hold a character. Re-check with `file -i`, or add `//TRANSLIT`/`//IGNORE`.

### How do I strip a UTF-8 BOM?

`iconv` won't always remove it; `sed '1s/^\xEF\xBB\xBF//' in.txt > out.txt` drops a leading BOM.

### What about Windows line endings while I'm at it?

Encoding and line endings are separate problems — see [dos2unix](/post/dos2unix-convert-line-endings/) for CRLF→LF.

## Summary

- Detect: `file -i file.txt`.
- Convert: `iconv -f FROM -t TO in > out` (`-f` = from, `-t` = to).
- Lossy targets: append `//TRANSLIT` or `//IGNORE`.
- In place: go via a temp file, never `> same-file`.
