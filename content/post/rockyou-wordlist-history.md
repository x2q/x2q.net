+++
title = "rockyou.txt: the history of the world's most famous wordlist (2026)"
date = 2026-07-03
slug = "rockyou-wordlist-history"
description = "Where rockyou.txt actually came from, why it became the default password-cracking wordlist, and what replaced it. A look at weakpass.com's current wordlist rankings — rockyou2021, rockyou2024, and the hashmob.net 'found' lists topping the charts in 2026."

[taxonomies]
tags = ["wordlists", "rockyou", "password-cracking", "hashcat", "weakpass", "security", "password-security"]

[extra]
summary = "rockyou.txt was born from a 2009 breach where 32 million passwords were stored in plaintext. It became the default pentest wordlist for a decade — but weakpass.com's 2026 rankings show it's no longer top-tier. Smaller, curated cuts (rockyou-65.txt) and continuously-refreshed 'found in the wild' lists from hashmob.net now outrank the original and its billion-entry sequels rockyou2021.txt and rockyou2024.txt."
faq = [
  { q = "What is rockyou.txt?", a = "rockyou.txt is a plaintext list of about 14.3 million real passwords, extracted from a December 2009 data breach of RockYou Inc., a company that made social-network widgets. The breach exposed roughly 32 million user accounts because RockYou stored passwords completely unhashed — plain text in the database. After deduplication, the leaked password column became the wordlist known as rockyou.txt." },
  { q = "Is rockyou.txt still useful in 2026?", a = "Yes, but it's no longer the best option. On weakpass.com's efficiency rankings, the original rockyou.txt sits in the middle tier (C), beaten by both much smaller curated subsets (rockyou-65.txt, 30K entries) and much larger, continuously-updated 'found password' lists from services like hashmob.net. It's still a reasonable starting point, but not the ceiling anymore." },
  { q = "Are rockyou2021.txt and rockyou2024.txt from new RockYou breaches?", a = "No. Despite the name, neither is new breach data from RockYou Inc. Both are community-compiled mega-lists — billions of entries merged and deduplicated from many prior leaks, wordlists, and algorithmically generated permutations — released on hacking forums and given the 'rockyou' name as a brand for 'the biggest compiled cracking dictionary,' not because they trace back to the original company." },
  { q = "What is weakpass.com?", a = "weakpass.com is a wordlist repository and cracking-community hub. It hosts hundreds of wordlists (from a few kilobytes to 145+ GB) with size, entry-count, and a letter-grade efficiency rank (S through F) based on cracking hit-rate rather than raw size, plus torrent downloads and an API." },
  { q = "What wordlist should I actually use in 2026?", a = "Start small and targeted, not big. weakpass.com's S-tier picks in 2026 are mostly small curated lists (rockyou-65.txt) or continuously-refreshed real-world 'found' lists (hashmob.net_2025.*.found) rather than the biggest files. Pair a modest list with a strong rule set (best64.rule, OneRuleToRuleThemAll) before reaching for a 100+ GB mega-list — rules on a good small list often out-crack raw size." }
]
+++

**TL;DR —** `rockyou.txt` is 14.3 million real passwords leaked in plaintext from a single company's 2009 database breach. It became the default wordlist for an entire generation of password cracking — bundled into Kali Linux, cited in every hashcat tutorial, immortalised as `/usr/share/wordlists/rockyou.txt.gz`. In 2026 it's still around, but it's no longer the best tool for the job: weakpass.com's current rankings put small curated cuts and continuously-refreshed real-world "found password" lists ahead of it. This post covers where it came from, why it won, and what's actually winning now.

## December 2009: a company that didn't hash its passwords

**RockYou Inc.** made Flash-based social-network widgets — SuperWall, funny photo apps — for MySpace and Facebook, at the peak of the platform-app boom. In December 2009, a **SQL injection** vulnerability in RockYou's site exposed its entire user database: roughly **32 million accounts**.

The breach would have been a footnote if not for one detail: RockYou stored account passwords as **plain text**. No hashing, no salting — just the password, verbatim, next to the email address. When the dump circulated, security researchers had something almost unheard of: **millions of real passwords, in the clear**, with no cracking required to see what people actually chose.

After deduplication, the unique password column came out to **~14.3–14.4 million entries**, and it started circulating as a plain `.txt` file under the name of the breached company: `rockyou.txt`.

## Why it became the default

Plenty of leaks happened before and after 2009. `rockyou.txt` specifically became the pentesting/CTF/red-team default for a few concrete reasons:

- **It was real, unhashed, human-chosen data.** Not a dictionary of English words, not a generated permutation set — actual passwords actual people typed, biased toward exactly the kind of predictable patterns (`iloveyou`, `password1`, birthdates, keyboard walks) that real accounts get compromised with.
- **The size was right for the hardware of the era.** 14.3M candidates ran to completion on a single CPU or early GPU in a reasonable time — useful, not just symbolic.
- **It was free and everywhere.** No account wall, no takedown that stuck. It got bundled into **SecLists** and shipped by default in **BackTrack**, then **Kali Linux**, at `/usr/share/wordlists/rockyou.txt.gz` — which put it on every pentester's machine whether they went looking for it or not.
- **English-majority bias matched the majority of early 2010s targets.** As cracking tooling globalised, this became a limitation, not just a feature — but at the time it was a hit rate advantage.

By the early 2010s, "run rockyou.txt against it" was the default first move in nearly every WPA handshake, hashed database dump, or CTF challenge involving a password hash.

## The name outlived the breach

Here's the part that surprises people: **rockyou2021.txt** and **rockyou2024.txt**, the huge sequel-named lists you'll find today, are **not** new breaches of RockYou Inc.

- **rockyou2021.txt** surfaced on a hacking forum in June 2021: roughly **8.46 billion entries**, compiled by merging dozens of prior leaks, wordlists, and algorithmically generated permutations (case variants, leetspeak substitutions, number suffixes) — not freshly stolen credentials.
- **rockyou2024.txt** followed the same pattern in 2024: roughly **9.95 billion entries**, another community mega-compilation.

The "rockyou" name got repurposed as a **brand for "the biggest compiled cracking dictionary of the moment,"** detached from its original meaning. Both are real, both are enormous, and both are worth having — but neither tells you anything about RockYou Inc.'s actual 2009 users. Treat the name as a genre label, not a provenance claim.

## What weakpass.com's rankings actually show in 2026

[weakpass.com](https://weakpass.com/wordlists) is the closest thing the cracking community has to a live wordlist leaderboard: hundreds of lists, each with size, entry count, and a letter-grade **efficiency rank (S through F)** — based on real-world crack hit-rate, not raw size. Pulling the current top of the board is more interesting than any single number:

| Wordlist | Rank | Size | Entries |
|---|:---:|---:|---:|
| `weakpass_4.merged.txt` | S | 37.72 GB | 3.58 B |
| `all-h.txt` | S | 28.51 GB | 2.72 B |
| `all-h.latin.txt` | S | 28.35 GB | 2.71 B |
| `triple-h.txt` | S | 21.82 GB | 2.13 B |
| `SAWL.txt` | S | 17.02 GB | 1.49 B |
| `cyclone.hashesorg.hashkiller.combined.txt` | S | 15.02 GB | 1.47 B |
| `hashpwn.txt` | S | 14.11 GB | 1.35 B |
| `Hashes.org` | S | 13.99 GB | 1.40 B |
| `dictionary_private.dic` | S | 2.66 GB | 206.28 M |
| `hashmob.net_2025.user.found` | S | 979.96 MB | 84.29 M |
| `rockyou-65.txt` | S | 238.80 KB | 30.29 K |
| `weakpass_4a.txt` | A | 81.37 GB | 8.44 B |
| `clatsdictionary.txt` | A | 71.55 GB | 7.87 B |
| `rockyou2024.txt` | B | 145.27 GB | 9.95 B |
| `rockyou2021.txt` | B | 91.62 GB | 8.46 B |
| **`rockyou.txt` (the original)** | **C** | **133.44 MB** | **14.34 M** |

That last row is the interesting one. The original `rockyou.txt` — the file that defined a decade of tutorials — ranks **below** both a 238-kilobyte curated cut of itself and the multi-billion-entry mega-compilations that borrowed its name. Three things are happening at once:

### 1. Rank measures hit-rate, not size

weakpass grades by **cracking efficiency**, not raw entry count. A tiny, carefully curated list that hits a high percentage of real-world passwords per candidate tried outranks a sprawling list padded with permutation noise. That's why `rockyou-65.txt` — a **30,290-entry, 238 KB** cut — sits in **S-tier**, the same bracket as 30+ GB mega-lists, while the 14.34-million-entry original sits three tiers lower.

### 2. Percentage-trimmed rockyou variants are a real technique

weakpass publishes a whole family of `rockyou-XX.txt` files — `rockyou-5.txt` up through `rockyou-75.txt` — each a probability-weighted cut of the original, kept in decreasing order of real-world frequency. `rockyou-5.txt` is 13 entries; `rockyou-75.txt` is 59,190. The idea: for a quick first pass against a large hash set, the top 5–15% of `rockyou.txt` by observed frequency often accounts for a disproportionate share of the crackable accounts. Try the tiny cut first; only reach for the full 14.3M-entry list, or the multi-billion-entry sequels, if the quick pass comes up empty.

| Cut | Size | Entries |
|---|---:|---:|
| `rockyou-5.txt` | 104 Bytes | 13 |
| `rockyou-25.txt` | 7.06 KB | 929 |
| `rockyou-50.txt` | 74.13 KB | 9.44 K |
| `rockyou-65.txt` | 238.80 KB | 30.29 K |
| `rockyou-75.txt` | 467.72 KB | 59.19 K |
| `rockyou.txt` (full) | 133.44 MB | 14.34 M |

### 3. "Found in the wild, this year" beats "leaked once, a decade ago"

The other pattern at the top of the S-tier: **`hashmob.net_2025.*.found`** lists. [hashmob.net](https://hashmob.net) is a live community hash-cracking hub — password hashes get submitted, the community cracks what it can, and the successfully cracked plaintexts get published back as wordlists, refreshed continuously. Because they represent **passwords people are choosing right now**, not passwords people chose in 2009, they carry a currency advantage no static leak can match, however large.

## What this means practically

If you're picking a wordlist in 2026, "biggest file" is the wrong heuristic:

1. **Start small and targeted.** A curated cut (`rockyou-65.txt`) or a fresh "found" list beats a 100 GB mega-file for a first pass — it finishes in seconds and often clears a meaningful chunk of weak accounts.
2. **Add rules before adding size.** `hashcat -a 0 -r best64.rule` (or the much larger `OneRuleToRuleThemAll.rule`) against a modest base list generates orders of magnitude more effective candidates than the same list run raw — and usually outperforms a bigger unmutated list for the same time budget.
3. **Reach for the mega-lists last.** `rockyou2021.txt`, `rockyou2024.txt`, `weakpass_4.merged.txt` and friends are worth having for exhaustive offline work against a hash set you can afford hours or days against — not as the first thing you try.
4. **The original `rockyou.txt` is still a fine baseline** — free, small enough to iterate on quickly, well understood — just no longer the ceiling.

> See [hashcat WiFi cracking in 2026](/post/hashcat-wifi-cracking-guide-2026/) for these wordlists in action against a real WPA handshake, and [25 years of Wi-Fi security](/post/hack-wireless-network/) for the broader attack-and-defence history.
