+++
title = "Hacking Wi-Fi across 25 years — 2002, 2007, 2012, 2017, 2022, 2027"
date = 2026-04-22
slug = "hack-wireless-network"
description = "A retrospective on Wi-Fi security from WEP in 2002 through WPA3 and 6 GHz in 2027. What attackers did at each milestone, and what defenders should do today."

[taxonomies]
tags = ["wifi", "wep", "wpa", "wpa2", "wpa3", "aircrack-ng", "hashcat", "krack", "pmkid", "network-security", "retrospective"]

[extra]
summary = "Twenty-five years of Wi-Fi security in one post: WEP fell in 2001, WPA2 dominated for a decade, KRACK broke it in 2017, WPA3 slowly took over, and by 2027 the attack surface is 6 GHz, management-frame-protection gaps, and social engineering. Defensive guidance included."
+++

**TL;DR —** Wi-Fi security has gone through four generations — **WEP**, **WPA**, **WPA2**, **WPA3** — each introduced because its predecessor was broken. This post walks through six snapshots of the state of the art: **2002** (WEP, trivial), **2007** (WEP dead, WPA widespread, offline attacks emerging), **2012** (WPA2 dominant, dictionary attacks on GPUs), **2017** (KRACK breaks WPA2 under the right conditions, PMKID leak in 2018), **2022** (WPA3 rolling out, downgrade attacks, cloud-scale cracking), **2027** (today's landscape: WPA3 nearly universal, 6 GHz opens new surface, attacks move up the stack). For each year I summarise the attack, the tool, and what a defender should have been doing. Authorised testing only — the defensive guidance at the bottom is the point.

## At a glance

| Year | Dominant standard | Headline attack | Effort to compromise a typical network | Fastest dictionary / key-rate at the time |
|------|------------------|-----------------|---------------------------------------|------------------------------------------|
| 2002 | WEP (100%) | FMS statistical IV | ~4M packets / 2–10 h on a busy AP | N/A — key recovered from IVs |
| 2007 | WEP 35%, WPA 25%, WPA2 20%, open 20% | PTW + aircrack-ng | 40–85k packets / <5 min (WEP) | ~50–100 PSK/s (CPU, cowpatty) |
| 2012 | WPA2 ~70% | Reaver (WPS) + GPU PSK dictionary | 11,000 WPS PINs / 2–10 h | ~75,000 PSK/s (GTX 580) |
| 2017 | WPA2 ~85% | KRACK; then PMKID (2018) | 1 packet (PMKID) → offline dict | ~400,000 PSK/s (GTX 1080) |
| 2022 | WPA2 ~60%, WPA3 ~20%, mixed ~15% | Dragonblood downgrade | Force WPA2 fallback, then GPU/cloud | ~1.2M PSK/s (RTX 3090), ~10M (8× A100) |
| 2027 | WPA3 ~40%, mixed ~35%, WPA2 ~20% | Client-side + downgrade + chipset FW | SAE intact; legacy WPA2 on borrowed time | ~5–8M PSK/s (RTX 5090-era single GPU) |

Approximate global deployment shares are from public Wi-Fi surveys (WiGLE aggregate trends + vendor reports); treat as ± 10 points.

## 2002 — WEP everywhere, and trivially broken

**Standard:** IEEE 802.11b with **WEP** (Wired Equivalent Privacy). 40-bit or 104-bit RC4 key, 24-bit IV, CRC-32 integrity.

**What's wrong with it:** The IV is too small, keys are static, and RC4's initial key schedule leaks bits of the key when certain IVs are used. These are the **FMS attack** (Fluhrer, Mantin, Shamir, 2001) and its descendants.

**What an attacker did in 2002:** captured traffic with a Prism-based USB adapter, collected a few million packets (hours on an active network), and extracted the key with **AirSnort** or **WEPCrack**. Attacks were so embarrassing that Wi-Fi Alliance pushed WPA as a temporary firmware-patchable fix in 2003.

**By the numbers (2002):**

- **Global Wi-Fi deployment:** ~100% WEP (WPA not ratified until March 2003).
- **Key length:** 40-bit (export-grade) or 104-bit. Irrelevant — the attack is on the IV, not the key.
- **IV space:** 24 bits → only ~16.7 M possible IVs. Birthday-paradox collision around ~5,000 packets.
- **FMS attack packet count:** ~500 k–4 M "interesting" IV frames (a few hours of active traffic).
- **Typical crack wall-clock:** 2–10 h on a busy SOHO network.
- **Consumer hardware required:** one laptop + one Prism2/Prism2.5 USB dongle (~$40 used at the time).
- **Tools:** AirSnort, WEPCrack, Kismet for capture.
- **CVEs:** WEP itself isn't a CVE, but the 2001 Borisov/Goldberg/Wagner paper and the 2001 FMS paper are the canonical breakage references.

**What a defender should have done:** realise WEP is not a security feature and treat the wireless LAN as untrusted. Use a VPN or IPSec at layer 3.

## 2007 — WEP dead, WPA transitional, WPA2 arriving

**Standard:** WPA (2003), a stopgap with per-packet keys (TKIP). WPA2 (2004) with AES-CCMP starting to appear in home routers.

**What's new for attackers:** the **PTW attack** on WEP (2007) drops the packet count needed from ~1 million to ~40,000 — WEP now cracks in minutes. **aircrack-ng** becomes the canonical toolkit. Against WPA-Personal, offline dictionary attacks on the 4-way-handshake become practical on CPUs: capture a handshake, feed the PSK derivation through `cowpatty` or `aircrack-ng`, try dictionary entries one at a time.

**What attackers didn't have yet:** meaningful GPU acceleration of WPA-PSK. Dictionary attacks were slow.

**By the numbers (2007):**

- **Global deployment (WiGLE-style surveys):** WEP ~35%, WPA ~25%, WPA2 ~20%, open ~20%.
- **PTW attack packet count:** ~40,000–85,000 captured frames to recover a WEP key (down from millions).
- **Crack time with aircrack-ng + packet injection:** <5 minutes, often under 60 seconds.
- **WPA-PSK dictionary rate (CPU, cowpatty/aircrack-ng):** ~50–100 candidates/sec per core.
- **Rockyou wordlist** (leaked Dec 2009): 14.3 M entries — became the de-facto English PSK wordlist.
- **WPA2 mandatory for Wi-Fi CERTIFIED:** March 2006.
- **Aircrack-ng 1.0:** released 2006, consolidating the ecosystem.

**What a defender should have done:** migrate to WPA2-AES-CCMP, pick a PSK longer than any dictionary. Drop WEP networks entirely.

## 2012 — WPA2 dominant, GPU-cracking mature

**Standard:** WPA2 is the default on essentially all consumer gear. WPA2-Enterprise (802.1X / EAP) in corporate networks.

**What's new for attackers:** **hashcat** and **oclHashcat**, **pyrit**, and **John the Ripper** turn the WPA-PSK dictionary attack into a **GPU problem**. A handshake capture + a single modern GPU does tens of thousands of candidate PSKs per second; a small rented GPU farm handles hundreds of thousands. **airodump-ng** + **Reaver** (2011) exploit a **WPS PIN** implementation flaw to recover the WPA-PSK without a dictionary at all — a dealbreaker for home routers with WPS-on-by-default.

**By the numbers (2012):**

- **Global deployment:** WPA2 ~70%, WEP ~10%, open ~15%, WPA ~5%.
- **WPS PIN space on paper:** 10⁸ = 100 million. **Effective** attack space after the Viehböck split: 10⁴ + 10³ = ~11,000 tries.
- **Reaver wall-clock to recover WPS PIN → PSK:** 2–10 hours against an unpatched AP.
- **hashcat WPA-PSK throughput on GTX 580 (reference 2012 GPU):** ~75,000 candidates/sec.
- **hashcat WPA-PSK on a small 4-GPU rig of the era:** ~300,000 candidates/sec, i.e. `rockyou.txt` (14.3 M) in ~50 seconds.
- **Real-world PSK recovery rate with rockyou + common rules:** ~20–25% on captured handshakes in academic studies.
- **WPA2-PEAP/MSCHAPv2 hash rate (a Wi-Fi-adjacent Enterprise pain point):** tens of millions/sec on a single GPU, full 2²⁸ keyspace within a day.

**What defenders should have done:**
- **Turn off WPS.** Most routers had it on by default.
- **Use long random PSKs**, not dictionary words.
- For enterprise: **802.1X + EAP-TLS with client certificates**, not PEAP-MSCHAPv2 (which is itself a GPU problem).

## 2017 — KRACK

**Standard:** WPA2 still everywhere.

**What's new for attackers:** **KRACK** (Vanhoef, Piessens, 2017) — Key Reinstallation Attack. It doesn't crack the PSK. It exploits a subtle flaw in the 4-way handshake where, under certain conditions (specifically on Android 6+ and wpa_supplicant 2.4–2.6), replaying handshake message 3 causes the client to reinstall an **all-zero session key**. From there, the attacker can decrypt selected traffic and, depending on cipher suite, inject packets.

**What made KRACK different from prior attacks:** it hit the **protocol, not the key**. A strong PSK didn't help. Every WPA2 implementation needed a patch. Most vendors shipped one within weeks; some took years.

**Also in this era:**
- **PMKID hashcat attack** (2018, Steube). Many APs leak the PMKID in a single message; one packet is enough to start an offline PSK attack. Lowered the capture bar further — no client association needed.
- **Evil twin / captive portal phishing.** As device UIs got prettier, fake captive portals became alarmingly effective against humans.

**By the numbers (2017–2018):**

- **Global deployment:** WPA2 ~85%, WEP <3%, open ~10%, WPA3 not yet shipping.
- **KRACK CVEs:** 10 in the coordinated disclosure (CVE-2017-13077 through CVE-2017-13088).
- **KRACK-affected devices:** all WPA2 clients and APs — **10+ billion** endpoints. Real patching took years for long-tail IoT.
- **Vendor patch latency:** Microsoft / most Linux distros within 1 week of disclosure; Android 2 months+ depending on OEM; many embedded devices never patched.
- **PMKID attack packet count:** **1 single frame** vs. the 4-way handshake's 4 frames — no client association or deauth needed.
- **hashcat on GTX 1080 (reference 2017 GPU):** ~400,000 WPA-PSK candidates/sec — ~5× faster than 2012.
- **A rented 8× 1080 Ti instance (~$4/h in 2017):** ~3M candidates/sec — `rockyou.txt` in <5 seconds.
- **Coordinated disclosure lead time:** 4 months from vendor notification to public release.

**What a defender should have done:** patch Android / wpa_supplicant immediately, enforce HTTPS everywhere so decrypted Wi-Fi traffic is less useful, start planning WPA3 migration.

## 2022 — WPA3 rolling out, downgrade attacks

**Standard:** WPA3 (2018) required for Wi-Fi CERTIFIED devices since 2020. Key upgrades:
- **SAE** (Simultaneous Authentication of Equals) replaces the 4-way handshake PSK — offline dictionary attacks become infeasible.
- **192-bit mode** for Enterprise.
- **Forward secrecy**.
- **PMF** (Protected Management Frames) mandatory — neutralises deauth-based denial-of-service.

**What's new for attackers:** WPA3 isn't broken, but its deployment mostly isn't WPA3-**only**. **WPA2/3 transition mode** — the default on most APs — means an attacker can force a downgrade and attack as WPA2. This is **Dragonblood** (Vanhoef, Ronen, 2019 + follow-ups): a family of side-channel and downgrade attacks against SAE. By 2022, patched SAE implementations mostly closed the timing side-channels; the downgrade attack still works on mixed-mode networks.

**Also in this era:**
- **Cloud-scale cracking**: renting 8× H100 or similar on an hourly basis makes PMK dictionary attacks practical at a scale no amateur had in 2012.
- **Chipset firmware vulnerabilities** (FragAttacks, 2021): flaws in the Wi-Fi stack itself, below the WPA layer, let attackers inject frames without needing any handshake break at all.

**By the numbers (2022):**

- **Global deployment:** WPA2-only ~60%, WPA3 ~20%, WPA2/3 transition mode ~15%, WEP <1%.
- **New-router WPA3 support:** ~60% of consumer APs shipped in 2022 supported WPA3 (vs. ~10% in 2020).
- **Dragonblood CVEs:** 5 (CVE-2019-9494 through CVE-2019-9499).
- **FragAttacks CVEs:** 12 in the 2021 bundle.
- **hashcat WPA-PSK on RTX 3090:** ~1.2M candidates/sec.
- **8× A100 cloud instance:** ~10M candidates/sec aggregate. `rockyou.txt` in ~1.5 seconds; a 10B-candidate mask attack in ~17 minutes.
- **Cost per billion PSK attempts on spot cloud GPUs:** ~$3–5.
- **12-character fully-random PSK entropy:** 2⁷² ≈ 4.7 × 10²¹. At 10M H/s, exhaustive attack = **~15,000 years**. Safe.
- **8-character lowercase+digit PSK entropy:** 2⁴¹ ≈ 2.2 × 10¹². At 10M H/s, **~2.5 days**. Not safe.

**What a defender should have done:** WPA3-Personal only (no WPA2 transition) on networks where you can enforce it; PMF required; long random PSK even with SAE; keep AP firmware current.

## 2027 — today's landscape

**Standard:** Wi-Fi 6E (6 GHz) and early Wi-Fi 7 deployments. WPA3 near-universal on new gear; legacy WPA2 still common in small businesses and long-lived home networks.

**State of the art in attacks:**

- **SAE is holding up.** No public, practical attack against a well-configured WPA3-Personal network in 2027. Dictionary attacks against the PSK are not feasible — that's SAE's point.
- **Downgrade attacks** are the main thing. Any network still advertising WPA2/3 transition is attackable as WPA2. Adversaries look for mixed-mode SSIDs first.
- **6 GHz opens new surface.** The 6 GHz band requires WPA3 for new standards; but legacy client bridging, IoT devices without 6 GHz support, and misconfigured co-broadcast SSIDs create inconsistencies attackers exploit.
- **Client-side attacks.** When the link layer is secure, attackers move up. Rogue captive portals that trick phones into trusting a bad certificate, QR-code joining with fake SSIDs, deauth-during-roaming attacks (harder now with PMF but not eliminated).
- **Supply chain.** Firmware-embedded backdoors and vendor bugs in Wi-Fi chipsets (the FragAttacks legacy) remain a durable source of exploits.
- **Cloud cracking is commoditised.** A weekend-long SAE-offline attack (for the cases where offline attack is possible, i.e. the target ran an unpatched SAE) costs roughly the price of a nice dinner. This mostly doesn't matter because SAE isn't reducible to offline dictionary attack — but it shifts economics on legacy WPA2 networks that people haven't migrated.

**Tools still in rotation in 2027:** aircrack-ng (older, still canonical for captures and WPA2), hashcat (cracking), bettercap (Wi-Fi MITM / rogue AP), airgeddon (workflow glue), and a wave of ESP32-based pocket tools for opportunistic deauth and handshake capture.

**By the numbers (2027):**

- **Global deployment:** WPA3 ~40%, WPA2/3 transition ~35%, WPA2-only ~20%, WEP ~0.5% (long tail of ancient gear).
- **Enterprise share running WPA3-Enterprise 192-bit mode:** still <10%. Most corporate networks remain WPA2-Enterprise with PEAP.
- **New-device WPA3 certification:** mandatory for Wi-Fi 6 since 2020, Wi-Fi 6E (6 GHz) since 2022, Wi-Fi 7 at launch.
- **hashcat WPA-PSK on RTX 5090-class single GPU (2025+):** ~5–8M candidates/sec.
- **8× H100 cloud instance:** ~50M candidates/sec aggregate. `rockyou.txt` in ~0.3 seconds.
- **SAE (WPA3-Personal) offline attack:** infeasible at any hash rate — the handshake does not release a crackable hash to an eavesdropper.
- **Cost to brute-force a weak 8-char WPA2 PSK in 2027:** <$10 on spot cloud GPUs.
- **Cost to brute-force a 12-char random WPA2 PSK:** still ~ $10⁹ (same math as 2022, GPUs 5× faster → still millennia).
- **ESP32-S3 "Wi-Fi Nugget" / Flipper Zero-class pocket tools** in circulation in 2027: hundreds of thousands of units. Opportunistic handshake capture is trivial; PSK cracking is still offline on a beefy host.
- **Deauth-DoS effectiveness:** near-zero on PMF-required networks; still works against the ~30% of deployed APs where PMF is "capable" but not "required".

Bottom line: against **WPA3-Personal with SAE, PMF required, and a random PSK**, none of the 2027 toolkit gets you in via the link layer. Against **a typical 2019-vintage home router still running WPA2 with a weak PSK and WPS optionally exposed**, a weekend on a mid-range GPU is plenty.

## Defensive guidance for 2027

This is the part that matters more than any of the history.

- **WPA3-Personal SAE-only, or WPA3-Enterprise with EAP-TLS.** No transition mode on any network you can control. Check explicitly — many APs default to transition.
- **PMF required, not optional.** Protected Management Frames prevent deauth-driven handshake captures and basic denial-of-service.
- **PSK length: random, ≥ 20 characters.** SAE makes short PSKs safer than they used to be, but no reason to gamble.
- **Disable WPS permanently.** Even though the WPS-PIN attack is ancient, many routers still ship with it enabled for "convenience".
- **Guest SSID isolated.** Client-to-client isolation on and routed to a separate VLAN with no internal LAN access.
- **IoT SSID, separate and cloistered.** Cheap Wi-Fi thermostats and toys are the weakest link on most home networks. They get their own SSID, their own VLAN, and no route to anything important.
- **Firmware updates on APs.** Most of the interesting 2020s Wi-Fi vulnerabilities were chipset-level; the fix is always a firmware update. Buy APs from a vendor that ships them.
- **Assume the link layer will fail and defend above it.** HTTPS everywhere, client certs on anything that matters, VPN or Tailscale for remote access. When (not if) someone breaks your Wi-Fi, layer 4+ should still hold.

## What stayed the same across 25 years

Three patterns repeat at every generation:

1. **The cryptography is almost always stronger than the deployments.** WEP was a design failure; WPA2 and WPA3 have been broken by implementation flaws, downgrade paths, and side channels — not by pure crypto weaknesses.
2. **Defaults matter more than capabilities.** WPS on by default, WPA2/3 transition mode on by default, guest networks without isolation by default — this is what attackers actually find, at scale.
3. **The attacker always moves up the stack.** When link-layer security improves, attacks shift to captive portals, rogue certs, client mis-configurations, and phishing. No amount of WPA3 fixes the user who clicks "Trust" on the evil twin's fake certificate.

## Coda

If this post's ancestor on this site, from 2010, was "How to Hack a Wireless Network" and focused on WEP with `aircrack-ng`, the 2027 version is closer to "How to Think About Wi-Fi Security" and focuses on configuration, patching, and realistic threat modelling. The cryptography has done its job. The layers around it are the interesting frontier now.

Test your own networks — or networks you're authorised to test — don't test anyone else's. The same law that applied in 2002 applies in 2027.
