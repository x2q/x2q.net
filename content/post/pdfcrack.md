+++
title = "pdfcrack — recover lost PDF passwords on Linux and macOS (2026)"
date = 2026-04-22
slug = "crack-password-protected-pdf-pdfcrack"
description = "How to use pdfcrack to recover a forgotten password on a protected PDF. Install, benchmark, dictionary vs brute-force, and when to switch to pdf2john + hashcat for AES-256 PDFs."

[taxonomies]
tags = ["pdfcrack", "pdf", "password-recovery", "password-cracking", "hashcat", "john-the-ripper", "linux", "macos", "security"]

[extra]
summary = "pdfcrack is a small, single-threaded CPU tool for recovering lost PDF user and owner passwords. Fine for 40-bit RC4 and small dictionary attacks; for 128/256-bit AES PDFs, migrate to pdf2john + hashcat on a GPU."
+++

**TL;DR —** **`pdfcrack`** is a command-line tool that recovers the **user password** or **owner password** of an encrypted PDF by brute-force or dictionary attack. It's small, written in C, runs on Linux/macOS/WSL, and handles every encryption profile PDF has shipped — 40-bit RC4, 128-bit RC4, 128-bit AES, 256-bit AES (PDF 1.7 + 2.0). It is **single-threaded and CPU-only**, so it is fast on the weak old RC4-40 encryption but increasingly slow as PDFs get modern. Install with `apt install pdfcrack` (Debian/Ubuntu), `brew install pdfcrack` (macOS), or build from source. When `pdfcrack` is too slow, switch to **`pdf2john` + `hashcat`** on a GPU.

This walkthrough assumes you have **authorisation to recover the password** on the PDF — your own document, a client's, or a legally-acquired file. Don't attack PDFs you don't own.

## User password vs owner password

PDF has two passwords:

- **User password** — required to **open and read** the document.
- **Owner password** — required to **remove restrictions** (print, copy, modify) on a document that opens without a user password.

Many "protected" PDFs are only owner-password-restricted: they open fine, but printing and copying are disabled by the reader. Those are trivial to unlock — `qpdf --decrypt` or any of the `pdftk`-style tools strip owner-only restrictions without needing to guess anything. `pdfcrack` is for the harder case: a **user-password-protected PDF you can't open at all**.

Check which you're dealing with:

```
$ qpdf --show-encryption document.pdf
R = 6
P = -3904
User password = 
Supplied password is owner password
extract for accessibility: allowed
extract for any purpose: not allowed
print low resolution: allowed
print high resolution: not allowed
modify document assembly: not allowed
modify forms: not allowed
modify annotations: not allowed
modify other: not allowed
stream encryption method: AESv3
string encryption method: AESv3
file encryption method: AESv3
```

- **`R = ...`** tells you the revision / profile. `R=2` = RC4-40, `R=3` = RC4-128, `R=4` = AES-128, `R=5/6` = AES-256.
- **"Supplied password is owner password"** + "User password = (empty)" means you can open it and just need to strip restrictions. Use `qpdf --decrypt --password='' input.pdf output.pdf` and you're done.

## Install

```
# Debian / Ubuntu / Mint / Kali
sudo apt install pdfcrack

# macOS (Homebrew)
brew install pdfcrack

# Arch / Manjaro
sudo pacman -S pdfcrack

# Fedora / RHEL
sudo dnf install pdfcrack

# From source
wget https://sourceforge.net/projects/pdfcrack/files/latest/download -O pdfcrack.tar.gz
tar xf pdfcrack.tar.gz && cd pdfcrack-*
make
sudo cp pdfcrack /usr/local/bin/
```

## Benchmark

```
$ pdfcrack -b
Benchmark:	Average Speed (calls / second):
MD5:			1728972.6
MD5_50 (fast):		 97879.3
MD5_50 (slow):		 69167.0

RC4 (40, static):	606555.3
RC4 (40, no check):	598050.0
RC4 (128, no check):	590141.7

Benchmark:	Average Speed (passwords / second):
PDF (40, user):		453510.2
PDF (40, owner):	220250.0
PDF (40, owner, fast):	499995.0

PDF (128, user):	 22000.0
PDF (128, owner):	 10408.7
PDF (128, owner, fast):	 22220.0
```

Translation:

- **RC4-40** (PDF 1.3, very old) — ~450k passwords/sec. Brute-force of a full 8-character alphanumeric space: ~1 week on one core.
- **RC4-128 / AES-128** — ~22k passwords/sec. Brute-force becomes unrealistic above length 6 with any charset.
- **AES-256 (R=5/6)** — even slower; `pdfcrack` does support it but effectively only for dictionary attacks against small wordlists.

If you need speed beyond this, you want `hashcat` on a GPU. Numbers at the bottom.

## Dictionary attack

```
pdfcrack -f document.pdf -w /usr/share/wordlists/rockyou.txt
```

- **`-f`** — target file.
- **`-w <file>`** — wordlist, one candidate per line.
- Optional **`-o`** — attack the owner password only (ignore user password). Default is to try user password first.
- Optional **`-u`** — attack user password only.

If you have context — the password is probably a first name, a year, a project code — assemble a smaller targeted list. Generic lists are a long shot once you're past the top ten thousand entries.

## Brute-force attack

```
pdfcrack -f document.pdf -c 'abcdefghijklmnopqrstuvwxyz0123456789' -n 4 -m 8
```

- **`-c <charset>`** — character set to try. Default includes a broad ASCII range.
- **`-n <min>`** — minimum length.
- **`-m <max>`** — maximum length.

Tune `-c` aggressively. If you know the password is all lowercase, don't give it uppercase. If you know it has a digit at the end, use a mask attack (hashcat territory, not pdfcrack).

## Resume a long run

```
pdfcrack -f document.pdf -w rockyou.txt -s /tmp/state.sav
```

`-s` writes periodic save files; if you kill pdfcrack and restart, pass `-l /tmp/state.sav` to resume.

## When to switch to hashcat

For any modern PDF (R=4, 5, or 6 — i.e. AES-128 or AES-256), `pdfcrack`'s single-core speed becomes the bottleneck. `pdf2john` + `hashcat` gets you two to three orders of magnitude more throughput on a GPU.

### Step 1: extract the hash

```
$ /usr/share/john/pdf2john.pl document.pdf > hash.txt
```

(On Debian/Ubuntu: `apt install john` provides `pdf2john.pl`.)

### Step 2: identify the hash mode

```
$ head -1 hash.txt
document.pdf:$pdf$5*6*256*-1028*1*16*...
```

Map the first two numbers:

- `$pdf$1*2*...` → **mode 10400** (PDF 1.1–1.3, RC4-40, user)
- `$pdf$1*2*...` with owner salt → **mode 10410 / 10420**
- `$pdf$2*3*...` → **mode 10500** (PDF 1.4–1.6, RC4-128 / AES-128)
- `$pdf$5*5*...` → **mode 10600** (PDF 1.7 r=5, AES-256)
- `$pdf$5*6*...` → **mode 10700** (PDF 1.7 r=6 / PDF 2.0, AES-256 with PBKDF2)

### Step 3: run hashcat

```
hashcat -m 10700 hash.txt /path/to/wordlist.txt
```

On a single modern GPU (e.g. RTX 4090):

- **Mode 10400 (RC4-40):** ~10 billion H/s — any practical password is recovered instantly.
- **Mode 10500 (RC4-128 / AES-128):** ~100 million H/s.
- **Mode 10700 (AES-256, PBKDF2):** ~50,000 H/s. This is by design — the PBKDF2 iterations make brute-force expensive.

For mode 10700, your attack strategy matters more than raw speed. Dictionary + rules + mask attacks targeted at likely password patterns are orders of magnitude more productive than exhaustive brute-force.

## Common gotchas

### "File seems encrypted but I can still open it without a password"

You're looking at owner-only restrictions. Use `qpdf --decrypt input.pdf output.pdf` — no cracking needed.

### pdfcrack runs but never finds anything

Three likely causes:

1. **Password is longer / more complex than your charset × length covers.** Increase `-m` and/or expand `-c`, or switch to a dictionary.
2. **Password contains non-ASCII characters.** pdfcrack's charset is ASCII by default; non-ASCII user passwords in old PDFs used varying encodings (PDFDocEncoding, UTF-16). Try `pdf2john` + hashcat, which handles the encoding properly.
3. **It's AES-256 (R=6) and you're being patient.** See speed notes above — realistic only with a dictionary.

### "Only AES-256 is supported" error or similar

Your `pdfcrack` build is old. Ubuntu LTS sometimes ships a version that doesn't fully handle R=6. Build from source or switch to `pdf2john` + `hashcat`.

### PDF opens but printing/copying is blocked

That's owner-password-restricted only. `qpdf --decrypt` without needing a password usually works:

```
qpdf --decrypt --password='' input.pdf output.pdf
```

## Defensive takeaway

For anything you want to stay encrypted in 2026, use **AES-256 with a PDF 2.0 (R=6) password**. That's the profile with PBKDF2 key derivation that makes offline attacks expensive on current hardware.

And, as always, the password's length matters more than anything else. A 20-character random passphrase is brute-force-intractable against any current GPU. A 6-character "clever substitution" password is a coffee break on an RTX 4090.

## FAQ

### Is pdfcrack still maintained?

Updated slowly. The codebase handles all currently shipped PDF encryption profiles; it just isn't where performance work is happening anymore (that's hashcat).

### Does pdfcrack use GPU?

No. CPU-only, single-threaded. For GPU work, use `pdf2john` + `hashcat`.

### Can pdfcrack recover the document if the creator cleared the user password but kept the owner password?

Yes — use `qpdf --decrypt` first; if that won't fully decrypt, `pdfcrack -o` attacks the owner password.

### Does pdfcrack leak my PDF anywhere?

No. It's local. Anything online-only ("crack my PDF at cloud-service-X.com") involves uploading the file, which you shouldn't do for confidential material.

### What if I only vaguely remember the password?

Write down what you remember — likely words, likely digits, likely length — and build a targeted wordlist or `hashcat` mask (`-a 3 ?l?l?l?l?l?d?d?d?d`). That beats any generic list.

### Can I recover text from an AES-256 PDF without the password?

No. AES-256 with PBKDF2 (R=6) is, to the best of public cryptanalysis, not broken. If the password is strong and lost, the contents are lost.

## Summary

- **Owner-password-only?** `qpdf --decrypt`, no cracking needed.
- **User-password-protected, old (R=2/3)?** `pdfcrack` with a dictionary works fine.
- **Modern (R=4/5/6)?** `pdf2john` + `hashcat` on a GPU, targeted attack.
- **Strong 20-character random?** Accept the loss.
