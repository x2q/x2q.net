+++
title = "fcrackzip — recover lost zip passwords on Linux, macOS, and Windows (2026)"
date = 2026-04-22
slug = "crack-password-encrypted-zip"
description = "How to use fcrackzip to recover a lost password on an encrypted .zip file. Install, brute-force, dictionary, and when to reach for zip2john + hashcat instead."

[taxonomies]
tags = ["fcrackzip", "zip", "password-recovery", "password-cracking", "hashcat", "john-the-ripper", "linux", "macos", "security"]

[extra]
summary = "fcrackzip is a small, old, command-line tool that recovers passwords on classic-ZipCrypto-encrypted .zip files. Brute-force or dictionary, runs everywhere, still useful in 2026 — with hashcat/john as the modern follow-up when it isn't fast enough."
+++

**TL;DR —** **`fcrackzip`** is a free, open-source command-line tool for recovering the password of an encrypted `.zip` file. It supports **brute-force** (over a user-defined charset and length) and **dictionary** attacks, works on Linux/macOS/WSL, and is the right first tool when you need to recover a forgotten password on a zip you legitimately own. It is only fast against **classic ZipCrypto** encryption; for the newer **AES-256** zip profile, `fcrackzip` will not work — you want `zip2john` + `hashcat` instead. Install with `apt install fcrackzip` (Debian/Ubuntu), `brew install fcrackzip` (macOS), or build from source.

This post walks through the practical cases. It assumes you have **authorisation to recover the password** — your own files, a client's, a CTF. Don't use it against zips you don't own.

## Install

```
# Debian / Ubuntu / Mint / Kali
sudo apt install fcrackzip

# macOS (Homebrew)
brew install fcrackzip

# Arch / Manjaro
sudo pacman -S fcrackzip

# Windows
# Use WSL2 + Ubuntu and `apt install fcrackzip`.
# A native .exe exists but is old — WSL is simpler.

# From source
git clone https://github.com/hyc/fcrackzip.git
cd fcrackzip && ./configure && make
sudo cp fcrackzip /usr/local/bin/
```

## Check what kind of encryption your zip uses first

`fcrackzip` only handles **classic ZipCrypto** (the original, weak PKZIP encryption). For modern **AES-128 / AES-256** zips (introduced by WinZip 9 in 2003, now default in some tools), `fcrackzip` will silently fail to find the password no matter how long you run it.

Quickest check with `zipinfo`:

```
$ zipinfo -v archive.zip | head -40
```

Look for `WinZip AES encryption, strength 3` (= AES-256). If you see that, skip to the hashcat section.

Or with `7z`:

```
$ 7z l -slt archive.zip | grep -i 'method\|encrypted'
Method = ZipCrypto Store          ← fcrackzip works
Method = AES-256 Deflate          ← fcrackzip will NOT work
```

## Basic brute-force

```
fcrackzip -v -b -c 'a1' -p aaaa -u archive.zip
```

- **`-v`** — verbose.
- **`-b`** — brute-force mode.
- **`-c 'a1'`** — charset. `a` = lowercase `a–z`, `A` = uppercase, `1` = digits, `!` = printable symbols. Combine: `'aA1!'` = all printable ASCII (94 chars).
- **`-p aaaa`** — starting password (defines minimum length = 4 here).
- **`-u`** — only report if the decrypted file "unzips" cleanly (filters false positives — ZipCrypto has a small CRC that many random passwords pass).

Length: `-p aaaaa` starts at 5 characters. `fcrackzip` doesn't have a `--max-length` flag; it increments the starting password through the charset forever, so **letting it run to "completion" at length 8 on the full printable ASCII charset is about 94⁸ ≈ 6×10¹⁵ candidates** — not realistic. You bound the attack by picking a reasonable max charset + length, or by using a dictionary.

## Dictionary attack

```
fcrackzip -v -D -u -p /usr/share/wordlists/rockyou.txt archive.zip
```

- **`-D`** — dictionary mode.
- **`-p <file>`** — wordlist file, one candidate per line.
- **`-u`** — verify via unzip, as before.

`rockyou.txt` is the standard 14 M-entry wordlist shipped with Kali and available everywhere. If you have context about the password (it's someone's name + year, it's a project codename), assemble a smaller targeted wordlist — hit rates are usually much higher than any generic list.

## Speed and what to expect

`fcrackzip` is single-threaded and CPU-bound. On a modern laptop you'll see roughly:

- **10–30 million ZipCrypto attempts per second per core** for a dictionary attack against a typical zip.
- Brute-force slightly faster because less string I/O.

That makes it fine for:

- **Dictionary attacks** against any reasonable wordlist.
- **Short brute-force** (4–6 chars alphanumeric).

It makes it not fine for:

- **Length 8+ with symbols** — you'll never finish.
- **AES-256 zips** — wrong tool.

## When to reach for hashcat instead

If `fcrackzip` is too slow, or the zip is AES-encrypted, migrate to `hashcat`. It's the general-purpose password-cracking tool, GPU-accelerated, and handles both ZipCrypto and AES WinZip hashes.

### Step 1: extract the hash with `zip2john`

`zip2john` is part of John the Ripper. Ubuntu: `apt install john`.

```
$ zip2john archive.zip > hash.txt
$ cat hash.txt
archive.zip:$zip2$*0*3*0*...*$/zip2$::archive.zip:secret.pdf:/path/to/archive.zip
```

### Step 2: feed it to hashcat

```
# ZipCrypto (mode 17200, 17210, 17220, 17225 depending on compression)
hashcat -m 17200 hash.txt /path/to/wordlist.txt

# AES-encrypted WinZip (mode 13600)
hashcat -m 13600 hash.txt /path/to/wordlist.txt
```

On a single modern discrete GPU (e.g. RTX 4090) you'll see:

- **ZipCrypto: ~5–10 billion H/s**
- **WinZip AES-256: ~10–50 million H/s** (much slower because AES is expensive and PBKDF2 iterations are involved)

hashcat's rule engine, mask attacks (`-a 3`), and combinator mode (`-a 1`) make it vastly more flexible than `fcrackzip`. For anything non-trivial it is the right tool.

## Common gotchas

### "PASSWORD FOUND!!!!: pw == abc" but `unzip` still asks for a password

You didn't use `-u`. fcrackzip's CRC check has false positives. Re-run with `-u` to verify candidates against a real decompression attempt.

### Different files in the same zip have different passwords

Classic PKZIP supports per-file passwords. `fcrackzip` attacks one file at a time; pass `-l <filename>` (or let it pick the first encrypted one) if you need to be specific.

### fcrackzip finds the password, but I still can't unzip

Character set / locale issue. If the password contains non-ASCII characters, the zip's creator may have used a different encoding than your terminal. Try `unzip -P "$(echo -n 'passwd' | iconv -t cp437)" archive.zip`.

### AES-encrypted and dictionary doesn't find it

hashcat + rules + a targeted wordlist is the move. See the migration steps above.

## Defensive takeaway

If you're generating zip files you want to stay encrypted: use **AES-256**, not ZipCrypto. Most modern tools (`7z`, `zip` from InfoZIP with `-e`, WinZip, Keka) give you AES if you ask. The default on `zip` unfortunately is still ZipCrypto on many systems. Check with `7z l -slt archive.zip` before shipping it.

And pick a password with length, not cleverness. `hashcat` doesn't care how weird your substitution pattern is; it only cares about entropy. A four-word passphrase (`correct-horse-battery-staple`-style, ~44 bits) is fine against offline ZipCrypto attacks; a random 12-character mixed password (~78 bits) is fine against GPU AES attacks. Anything shorter is recoverable.

## FAQ

### Is fcrackzip legal?

Recovering passwords on files you own or are authorised to access is legal in every jurisdiction I'm aware of. Doing it on someone else's file without authorisation is unauthorised access — the same law that applies to any other computer intrusion.

### Is fcrackzip maintained?

Barely. The codebase has been stable for fifteen-plus years. For modern work, the combination of `zip2john` + `hashcat` has eclipsed it.

### Can fcrackzip use a GPU?

No. `fcrackzip` is CPU-only. If GPU is what you have, go straight to hashcat.

### Does fcrackzip handle .7z, .rar, .gpg files?

No — only classic PKZIP `.zip`. For `.7z`, use `7z2john` + hashcat (mode 11600). For `.rar`, `rar2john` + hashcat (mode 12500 / 13000). For `.gpg`, `gpg2john` + hashcat (mode 17010+).

### How do I generate a targeted wordlist?

`hashcat`'s maskprocessor (`mp64`), `crunch`, and `cewl` (crawls a site for candidate words) are all worth knowing. For recovering a specific forgotten password, writing down what you remember about it — length, likely words, likely numbers — and building a mask attack from that is the highest-yield approach.

## Summary

- `fcrackzip` + `-D` + a wordlist is the right first try.
- If that doesn't work and it's ZipCrypto: `fcrackzip` + `-b` with a narrow charset and short length.
- If that doesn't work or it's AES: `zip2john` + `hashcat` on a GPU.
- If that doesn't work: your password was strong enough. That's the system working as intended.
