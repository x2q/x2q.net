+++
title = "Recover RAR, 7z, and ZIP archive passwords on Linux (2026)"
date = 2009-03-22
updated = 2026-06-06
slug = "crack-rar-7z-zip-passwords-linux"
description = "Recover a forgotten password on a RAR, 7z, or ZIP archive on Linux: extract the hash with John the Ripper's *2john tools, then crack it with hashcat on a GPU. The modern replacement for rarcrack."

[taxonomies]
tags = ["rar", "7z", "zip", "hashcat", "john-the-ripper", "password-recovery", "password-cracking", "security", "linux"]

[extra]
summary = "rarcrack is long abandoned. The 2026 way to recover a RAR/7z/ZIP password is to extract a hash with John the Ripper's rar2john/7z2john/zip2john, then run it through hashcat (GPU) or john. Dictionary first, then masks. Covers the right hashcat mode for each format."
+++

**TL;DR —** extract a hash with `rar2john` / `7z2john` / `zip2john`, then crack it with `hashcat` (GPU) or `john`. Dictionary attack first, then a targeted mask. This replaces the old `rarcrack` tool, which is unmaintained and CPU-only.

> The 2009 version of this post used **rarcrack** — abandoned for over a decade. The modern, far faster approach is John the Ripper's hash extractors + hashcat on a GPU. For the ZIP-specific deep dive, see the [fcrackzip post](/post/crack-password-encrypted-zip/); this one covers RAR and 7z too. Only do this on archives you own or are authorised to access.

## The two-step approach

Modern crackers don't attack the archive directly. You **extract a hash** that represents the password check, then throw a cracker at the hash. The extractors ship with John the Ripper:

```
sudo apt install john          # provides rar2john, zip2john, and the *2john scripts
sudo apt install hashcat        # GPU-accelerated cracker
```

## RAR

```
rar2john archive.rar > hash.txt
cat hash.txt
```

The hash format tells you the RAR version. Pick the hashcat mode:

```
# RAR3 (-hp, older):
hashcat -m 12500 hash.txt /usr/share/wordlists/rockyou.txt

# RAR5 (modern):
hashcat -m 13000 hash.txt /usr/share/wordlists/rockyou.txt
```

## 7-Zip

`7z2john` is a Perl script (install `libcompress-raw-lzma-perl` if it complains):

```
7z2john archive.7z > hash.txt        # or: 7z2john.pl archive.7z > hash.txt
hashcat -m 11600 hash.txt /usr/share/wordlists/rockyou.txt
```

7-Zip uses AES-256 with many KDF iterations, so it's **slow** to crack — a good wordlist matters far more than raw speed here.

## ZIP

```
zip2john archive.zip > hash.txt
```

Which mode depends on the encryption:

```
# Classic ZipCrypto (weak, old PKZIP):
hashcat -m 17200 hash.txt /usr/share/wordlists/rockyou.txt

# WinZip AES (modern, strong):
hashcat -m 13600 hash.txt /usr/share/wordlists/rockyou.txt
```

For ZipCrypto specifically, the lightweight `fcrackzip` is also an option — [covered separately](/post/crack-password-encrypted-zip/).

## Dictionary first, then masks

Most recoveries succeed with a wordlist — start there (`rockyou.txt` ships with Kali, or grab it anywhere). If you remember the *shape* of the password, a **mask attack** is far more efficient than blind brute force:

```
# 8 chars: capital + 5 lowercase + 2 digits, e.g. "Summer26"
hashcat -m 13000 -a 3 hash.txt '?u?l?l?l?l?l?d?d'
```

Add rules to a dictionary run to cover common mutations:

```
hashcat -m 13000 hash.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

## What to expect

- **GPU vs CPU:** hashcat on a modern GPU is orders of magnitude faster than the old CPU tools. ZipCrypto cracks at billions/sec; RAR5 and 7z are deliberately slow (strong KDF), so lean on good wordlists and masks rather than exhaustive brute force.
- **Resume:** hashcat checkpoints automatically — `--restore` continues an interrupted run.
- **Find the running guess:** press `s` for status during a run.

## FAQ

### hashcat says "No hashes loaded" or "Token length exception"

The extracted hash includes a prefix the mode must match (e.g. RAR3 vs RAR5). Check the start of `hash.txt` against the mode you chose; `hashcat --identify hash.txt` can help.

### Is this legal?

Recovering a password on an archive you own or are authorised to access is fine. Doing it to someone else's file without permission is unauthorised access — the usual computer-misuse laws apply.

### Strong password, dictionary failed — now what?

If it's a long random password on RAR5/7z/WinZip-AES, it may simply be out of reach — that's the encryption working as intended. Spend your effort on a smarter wordlist/mask built from what you remember, not on brute-forcing length.

## Summary

- Extract: `rar2john` / `7z2john` / `zip2john` → `hash.txt`.
- Crack: hashcat modes — RAR3 `12500`, RAR5 `13000`, 7z `11600`, ZipCrypto `17200`, WinZip-AES `13600`.
- Wordlist + rules first, then targeted masks. rarcrack is obsolete — don't bother.
